"""
Gemini API 调试测试
用于调试图片生成问题
"""

import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# 添加 src 目录到路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.image_gen.gemini_client import GeminiImageGenerator

# 加载环境变量
load_dotenv()

async def test_generate_simple():
    """简单测试：生成一张人物参考图"""
    logger.info("=== 开始测试 Gemini 图片生成 ===")

    # 初始化客户端
    api_key = os.getenv("GEMINI_API_KEY")
    base_url = os.getenv("GEMINI_API_BASE_URL", "https://generativelanguage.googleapis.com")
    model = os.getenv("GEMINI_MODEL", "gemini-3-pro-image-preview")

    logger.info(f"API Key: {api_key[:20]}...")
    logger.info(f"Base URL: {base_url}")
    logger.info(f"Model: {model}")

    client = GeminiImageGenerator(
        api_key=api_key,
        base_url=base_url,
        model=model
    )

    # 测试简单的人物生成
    try:
        logger.info("\n--- 生成人物参考图 ---")
        prompt = """生成一个日漫风格的漫画人物角色参考图。

角色名称：测试角色
角色描述：一个年轻的女孩，黑色长发，穿着蓝色校服

要求：
1. 全身正面照，展示完整服装和特征
2. 简洁的背景（纯色或渐变）
3. 清晰的轮廓，便于后续参考使用
4. 保持角色一致性，表情自然平静
"""

        result = await client.generate_with_references(
            prompt=prompt,
            image_refs=None,
            image_size="4K",
            aspect_ratio="3:4",
            timeout=120
        )

        logger.success(f"生成成功！图片数据长度: {len(result)}")
        logger.info(f"图片前缀: {result[:50]}...")

        # 保存图片
        output_dir = Path("output/test")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "test_character.png"

        client.save_base64_image(result, output_path)
        logger.success(f"图片已保存到: {output_path}")

    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())


async def test_generate_with_raw_response():
    """测试并打印完整的 API 响应，用于调试"""
    logger.info("\n=== 测试原始 API 响应 ===")

    import httpx

    api_key = os.getenv("GEMINI_API_KEY")
    base_url = os.getenv("GEMINI_API_BASE_URL", "https://generativelanguage.googleapis.com")
    model = os.getenv("GEMINI_MODEL", "gemini-3-pro-image-preview")

    endpoint = f"{base_url.rstrip('/')}/v1beta/models/{model}:generateContent"

    payload = {
        "contents": [{
            "role": "user",
            "parts": [
                {"text": "生成一个日漫风格的漫画人物"}
            ]
        }],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "imageSize": "4K",
                "aspectRatio": "3:4"
            }
        }
    }

    logger.info(f"请求 URL: {endpoint}")
    logger.info(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{endpoint}?key={api_key}",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            logger.info(f"状态码: {response.status_code}")

            if response.status_code != 200:
                logger.error(f"请求失败: {response.text}")
                return

            result = response.json()

            # 打印完整响应用于调试
            logger.info("\n=== 完整 API 响应 ===")
            logger.info(json.dumps(result, ensure_ascii=False, indent=2))

            # 分析响应结构
            logger.info("\n=== 响应结构分析 ===")
            if "candidates" in result:
                logger.info(f"candidates 数量: {len(result['candidates'])}")
                if len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    logger.info(f"candidate keys: {candidate.keys()}")

                    if "content" in candidate:
                        content = candidate['content']
                        logger.info(f"content keys: {content.keys()}")

                        if "parts" in content:
                            parts = content['parts']
                            logger.info(f"parts 数量: {len(parts)}")

                            for i, part in enumerate(parts):
                                logger.info(f"\n--- Part {i} ---")
                                logger.info(f"part keys: {part.keys()}")
                                for key, value in part.items():
                                    if key == "inline_data":
                                        logger.info(f"inline_data.mime_type: {value.get('mime_type')}")
                                        logger.info(f"inline_data.data 长度: {len(value.get('data', ''))}")
                                    else:
                                        logger.info(f"{key}: {str(value)[:200]}...")

    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    # 配置日志
    logger.remove()
    logger.add(
        sys.stderr,
        level="DEBUG",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )

    # 运行测试
    # asyncio.run(test_generate_with_raw_response())
    asyncio.run(test_generate_simple())
