"""
Gemini API 客户端
参考 app.js:1329-1340 和 app.js:1943 的实现
"""

import base64
import httpx
import json
import re
from typing import List, Optional, Dict, Any
from pathlib import Path
from loguru import logger


class GeminiImageGenerator:
    """Gemini 图片生成客户端，参考 app.js 的实现"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://generativelanguage.googleapis.com",
        model: str = "gemini-3-pro-image-preview"
    ):
        """
        初始化 Gemini 客户端

        Args:
            api_key: API 密钥
            base_url: API 基础地址
            model: 模型名称（默认 gemini-3-pro-image-preview）
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.endpoint = f"{self.base_url}/v1beta/models/{self.model}:generateContent"

    async def generate_with_references(
        self,
        prompt: str,
        image_refs: Optional[List[str]] = None,
        image_size: str = "2K",
        aspect_ratio: str = "3:4",
        timeout: int = 120
    ) -> str:
        """
        生成漫画图片，携带参考图

        参考 app.js:1318-1340 的实现逻辑

        Args:
            prompt: 文本提示词
            image_refs: base64 编码的参考图列表（人物、场景等）
            image_size: 图像大小（1K/2K/4K）
            aspect_ratio: 长宽比
            timeout: 超时时间（秒）

        Returns:
            base64 编码的生成图片
        """
        # 构建 parts 数组
        parts: List[Dict[str, Any]] = [{"text": prompt}]

        # 添加参考图（对应 app.js 中的 inline_data）
        if image_refs:
            for img_b64 in image_refs:
                # 如果包含 data URL 前缀，去除它
                if img_b64.startswith("data:"):
                    img_b64 = img_b64.split(",")[1]

                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": img_b64
                    }
                })

        # 构建请求 payload（对应 app.js:1318-1326）
        payload = {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],  # 支持文本和图片混合响应
                "imageConfig": {
                    "imageSize": image_size,
                    "aspectRatio": aspect_ratio
                }
            }
        }

        logger.info(f"发送 Gemini API 请求: {self.endpoint}")
        logger.debug(f"Payload: {payload}")

        try:
            # 发送请求（对应 app.js:1329-1340）
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.endpoint}?key={self.api_key}",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                result = response.json()

            # 解析返回的图片数据
            # （参考 app.js: 遍历 parts 数组查找图片）
            if "candidates" not in result or len(result["candidates"]) == 0:
                raise ValueError("API 返回结果为空")

            # 遍历所有 parts，查找图片数据
            parts = result["candidates"][0]["content"]["parts"]
            image_base64 = None
            mime_type = "image/jpeg"

            for part in parts:
                # 检查是否有 inlineData（直接图片数据）
                if "inlineData" in part:
                    inline_data = part["inlineData"]
                    if inline_data.get("mimeType", "").startswith("image/"):
                        image_base64 = inline_data["data"]
                        mime_type = inline_data["mimeType"]
                        break
                # 检查 text 中是否包含 Markdown 格式的图片
                # 例如: ![image](data:image/png;base64,...)
                elif "text" in part:
                    text = part["text"]
                    # 匹配 data:image 格式的图片
                    match = re.search(r'!\[.*?\]\((data:image/[^)]+)\)', text)
                    if match:
                        data_url = match.group(1)
                        # 提取 mime_type 和 base64 数据
                        if "," in data_url:
                            mime_prefix, image_base64 = data_url.split(",", 1)
                            mime_type = mime_prefix.split(":")[1].split(";")[0]
                        break

            if image_base64 is None:
                # 没有找到图片，返回完整响应用于调试
                logger.error(f"API 响应中未找到图片数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
                raise ValueError("API 响应中未找到图片数据")

            logger.success("图片生成成功")
            return f"data:{mime_type};base64,{image_base64}"

        except httpx.HTTPError as e:
            logger.error(f"HTTP 请求失败: {e}")
            raise
        except KeyError as e:
            logger.error(f"解析 API 响应失败，缺少键: {e}")
            logger.error(f"API 响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
            # 提供更详细的错误信息
            if "error" in result:
                error_msg = result.get("error", {}).get("message", str(result))
                raise ValueError(f"API 返回错误: {error_msg}")
            raise ValueError(f"API 响应格式错误，缺少键: {e}")

    async def generate_character_reference(
        self,
        character_name: str,
        description: str,
        style: str = "日漫风格",
        image_size: str = "2K",
        aspect_ratio: str = "3:4"
    ) -> str:
        """
        生成人物参考图

        Args:
            character_name: 角色名称
            description: 角色描述
            style: 漫画风格
            image_size: 图像大小
            aspect_ratio: 长宽比

        Returns:
            base64 编码的图片
        """
        prompt = f"""生成一个{style}的漫画人物角色参考图。

角色名称：{character_name}
角色描述：{description}

要求：
1. 全身正面照，展示完整服装和特征
2. 简洁的背景（纯色或渐变）
3. 清晰的轮廓，便于后续参考使用
4. 保持角色一致性，表情自然平静
"""

        return await self.generate_with_references(
            prompt=prompt,
            image_refs=None,
            image_size=image_size,
            aspect_ratio=aspect_ratio
        )

    async def generate_scene_reference(
        self,
        scene_name: str,
        description: str,
        style: str = "日漫风格",
        image_size: str = "2K",
        aspect_ratio: str = "16:9"
    ) -> str:
        """
        生成场景参考图

        Args:
            scene_name: 场景名称
            description: 场景描述
            style: 漫画风格
            image_size: 图像大小
            aspect_ratio: 长宽比

        Returns:
            base64 编码的图片
        """
        prompt = f"""生成一个{style}的漫画场景参考图。

场景名称：{scene_name}
场景描述：{description}

要求：
1. 宽视角，展示完整场景
2. 无人物，仅环境和建筑
3. 色彩协调，光线自然
4. 适合作为漫画背景使用
"""

        return await self.generate_with_references(
            prompt=prompt,
            image_refs=None,
            image_size=image_size,
            aspect_ratio=aspect_ratio
        )

    async def generate_comic_panel(
        self,
        prompt: str,
        character_refs: Optional[List[str]] = None,
        scene_refs: Optional[List[str]] = None,
        image_size: str = "2K",
        aspect_ratio: str = "3:4"
    ) -> str:
        """
        生成漫画分镜图片

        Args:
            prompt: 分镜描述
            character_refs: 人物参考图（base64）
            scene_refs: 场景参考图（base64）
            image_size: 图像大小
            aspect_ratio: 长宽比

        Returns:
            base64 编码的图片
        """
        # 合并所有参考图
        all_refs = []
        if character_refs:
            all_refs.extend(character_refs)
        if scene_refs:
            all_refs.extend(scene_refs)

        return await self.generate_with_references(
            prompt=prompt,
            image_refs=all_refs if all_refs else None,
            image_size=image_size,
            aspect_ratio=aspect_ratio
        )

    def save_base64_image(self, base64_data: str, output_path: Path) -> Path:
        """
        保存 base64 图片到文件

        Args:
            base64_data: base64 编码的图片（可能包含 data URL 前缀）
            output_path: 输出文件路径

        Returns:
            保存的文件路径
        """
        # 如果包含 data URL 前缀，去除它
        if base64_data.startswith("data:"):
            base64_data = base64_data.split(",")[1]

        # 解码并保存
        image_data = base64.b64decode(base64_data)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'wb') as f:
            f.write(image_data)

        logger.info(f"图片已保存: {output_path}")
        return output_path
