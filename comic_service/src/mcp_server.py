"""
漫画服务 MCP 服务器
提供小说转漫画的 MCP 接口

工作流程：
1. AI 工具调用 get_workflow_guide 获取工作流程和 JSON Schema
2. AI 工具根据小说内容生成 JSON（使用提供的 Schema）
3. AI 工具调用 generate_character_reference 生成角色参考图
4. AI 工具调用 generate_scene_reference 生成场景参考图
5. AI 工具调用 generate_comic_page，传入 JSON，MCP 生成图片并返回地址
"""

import os
import sys
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from loguru import logger
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
)

from .image_gen.gemini_client import GeminiImageGenerator
from .image_gen.character_manager import CharacterManager
from .image_gen.scene_manager import SceneManager
from .models.comic_schema import Page
from .models.schemas import get_workflow_guide, get_json_schema_guide, COMIC_PAGE_EXAMPLE

# 配置日志 - 使用 stderr 输出避免编码问题
logger.remove()
logger.add(lambda msg: print(msg, file=sys.stderr, end=''), level="INFO")


class ComicMCPServer:
    """漫画服务 MCP 服务器"""

    def __init__(self):
        """初始化服务器"""
        self.server = Server("comic-service")

        # 加载配置
        self.config = self._load_config()

        # 初始化 Gemini 客户端
        api_key = os.getenv("GEMINI_API_KEY", self.config.get("api_key"))
        base_url = os.getenv("GEMINI_API_BASE_URL", self.config.get("api_base_url"))
        model = self.config.get("model", "gemini-3-pro-image-preview")

        if not api_key or api_key == "YOUR_API_KEY_HERE":
            logger.warning("⚠️  GEMINI_API_KEY 未设置！请在 .env 文件中配置")

        self.gemini_client = GeminiImageGenerator(
            api_key=api_key,
            base_url=base_url,
            model=model
        )

        # 初始化管理器
        ref_path = Path(self.config.get("storage", {}).get("reference_images_path", "./config/references"))
        self.character_manager = CharacterManager(
            gemini_client=self.gemini_client,
            storage_dir=ref_path / "characters"
        )
        self.scene_manager = SceneManager(
            gemini_client=self.gemini_client,
            storage_dir=ref_path / "scenes"
        )

        # 注册工具
        self._register_tools()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        config_path = Path(__file__).parent.parent / "config" / "gemini_config.json"

        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        # 默认配置
        return {
            "api_key": "",
            "model": "gemini-3-pro-image-preview",
            "storage": {
                "reference_images_path": "./config/references",
                "output_images_path": "./output/pages"
            }
        }

    def _register_tools(self):
        """注册所有 MCP 工具"""

        @self.server.list_resources()
        async def handle_list_resources() -> list[Resource]:
            """列出所有可用资源"""
            return [
                Resource(
                    uri="file:///workflow",
                    name="工作流程指引",
                    description="漫画生成的工作流程和 JSON Schema",
                    mimeType="text/plain"
                ),
                Resource(
                    uri="file:///characters",
                    name="已创建的角色",
                    description="所有已生成参考图的角色列表",
                    mimeType="application/json"
                ),
                Resource(
                    uri="file:///scenes",
                    name="已创建的场景",
                    description="所有已生成参考图的场景列表",
                    mimeType="application/json"
                ),
            ]

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """读取资源"""
            if uri == "file:///workflow":
                return get_workflow_guide()
            elif uri == "file:///characters":
                chars = self.character_manager.list_characters()
                return json.dumps([c.model_dump() for c in chars], ensure_ascii=False, indent=2, default=str)
            elif uri == "file:///scenes":
                scenes = self.scene_manager.list_scenes()
                return json.dumps([s.model_dump() for s in scenes], ensure_ascii=False, indent=2, default=str)
            return "{}"

        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """列出所有可用工具"""
            return [
                # 工作流程工具
                Tool(
                    name="get_workflow_guide",
                    description="获取漫画生成的工作流程指引 - 首次使用时必读，包含完整的步骤说明和 JSON Schema",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    }
                ),
                Tool(
                    name="get_json_schema",
                    description="获取漫画页面的 JSON Schema 和示例 - 了解如何格式化漫画数据",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    }
                ),

                # 参考图生成工具
                Tool(
                    name="generate_character_reference",
                    description="生成人物参考图 - 为每个角色创建固定的参考图片，确保多页中人物视觉一致",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "character_name": {
                                "type": "string",
                                "description": "角色名称"
                            },
                            "description": {
                                "type": "string",
                                "description": "角色详细的外貌描述（发色、发型、服装、年龄、体型等）"
                            },
                            "visual_features": {
                                "type": "object",
                                "description": "视觉特征（可选）",
                                "properties": {
                                    "hair_color": {"type": "string", "description": "发色"},
                                    "hair_style": {"type": "string", "description": "发型"},
                                    "clothing": {"type": "string", "description": "服装"},
                                    "age_range": {"type": "string", "description": "年龄范围"},
                                    "facial_features": {"type": "string", "description": "面部特征"}
                                }
                            },
                            "style": {
                                "type": "string",
                                "description": "漫画风格",
                                "default": "日漫风格"
                            }
                        },
                        "required": ["character_name", "description"]
                    }
                ),
                Tool(
                    name="generate_scene_reference",
                    description="生成场景参考图 - 为重要场景创建固定的参考图片",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "scene_name": {
                                "type": "string",
                                "description": "场景名称"
                            },
                            "description": {
                                "type": "string",
                                "description": "场景详细描述（环境、光线、氛围等）"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "场景标签（如：城市、街道、白天等）"
                            },
                            "style": {
                                "type": "string",
                                "description": "漫画风格",
                                "default": "日漫风格"
                            }
                        },
                        "required": ["scene_name", "description"]
                    }
                ),

                # 核心工具：生成漫画图片
                Tool(
                    name="generate_comic_page",
                    description="""生成漫画图片 - 通过 JSON 文件路径生成单个漫画页面

⚠️ JSON 文件格式要求（必须遵守）：
1. 对话中的引号必须转义："text": "他说: \"你好\""
2. 数组末尾不要逗号："panels": [{...}] 而不是 [{...},]
3. 必须使用双引号，不能用单引号
4. 确保所有括号和引号匹配

JSON 文件示例：{"page_number": 1, "panels": [{"panel_number": 1, "description": "画面描述", "characters": [], "dialogues": [], "background": "背景", "camera_angle": "中景"}]}

服务会自动从文件读取 JSON 并尝试修复格式错误""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "json_path": {
                                "type": "string",
                                "description": "JSON 文件路径（相对于项目根目录的路径，如 output/page_001.json）"
                            },
                            "image_size": {
                                "type": "string",
                                "description": "图像大小",
                                "enum": ["1K", "2K", "4K"],
                                "default": "4K"
                            },
                            "aspect_ratio": {
                                "type": "string",
                                "description": "长宽比",
                                "enum": ["1:1", "16:9", "9:16", "3:4", "4:3", "3:2", "2:3", "21:9"],
                                "default": "3:4"
                            },
                            "style": {
                                "type": "string",
                                "description": "漫画风格",
                                "default": "日漫风格"
                            }
                        },
                        "required": ["json_path"]
                    }
                ),

                # 管理工具
                Tool(
                    name="list_characters",
                    description="列出所有已创建的角色参考图",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="list_scenes",
                    description="列出所有已创建的场景参考图",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="update_character_reference",
                    description="更新人物参考图 - 如果对现有角色的参考图不满意，可以重新生成",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "character_id": {
                                "type": "string",
                                "description": "角色 ID（使用 list_characters 查看）"
                            },
                            "new_description": {
                                "type": "string",
                                "description": "新的外貌描述"
                            }
                        },
                        "required": ["character_id", "new_description"]
                    }
                ),
                Tool(
                    name="regenerate_page",
                    description="重新生成指定页面 - 通过 JSON 文件路径重新生成漫画页面（会覆盖原文件）",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "json_path": {
                                "type": "string",
                                "description": "JSON 文件路径（相对于项目根目录的路径，如 output/page_001.json）"
                            },
                            "image_size": {
                                "type": "string",
                                "description": "图像大小",
                                "enum": ["1K", "2K", "4K"],
                                "default": "4K"
                            },
                            "aspect_ratio": {
                                "type": "string",
                                "description": "长宽比",
                                "enum": ["1:1", "16:9", "9:16", "3:4", "4:3", "3:2", "2:3", "21:9"],
                                "default": "3:4"
                            },
                            "style": {
                                "type": "string",
                                "description": "漫画风格",
                                "default": "日漫风格"
                            }
                        },
                        "required": ["json_path"]
                    }
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
            """处理工具调用"""

            try:
                # 工作流程工具
                if name == "get_workflow_guide":
                    return await self._get_workflow_guide()

                elif name == "get_json_schema":
                    return await self._get_json_schema()

                # 参考图生成
                elif name == "generate_character_reference":
                    return await self._generate_character_reference(**arguments)

                elif name == "generate_scene_reference":
                    return await self._generate_scene_reference(**arguments)

                # 核心工具
                elif name == "generate_comic_page":
                    return await self._generate_comic_page(**arguments)

                # 管理工具
                elif name == "list_characters":
                    return await self._list_characters()

                elif name == "list_scenes":
                    return await self._list_scenes()

                elif name == "update_character_reference":
                    return await self._update_character_reference(**arguments)

                elif name == "regenerate_page":
                    return await self._regenerate_page(**arguments)

                else:
                    return [TextContent(type="text", text=f"未知工具: {name}")]

            except Exception as e:
                logger.error(f"工具调用失败 {name}: {e}")
                return [TextContent(type="text", text=f"错误: {str(e)}")]

    # ========== 工具实现 ==========

    async def _get_workflow_guide(self) -> list[TextContent]:
        """获取工作流程指引"""
        guide = get_workflow_guide()
        return [TextContent(type="text", text=guide)]

    async def _get_json_schema(self) -> list[TextContent]:
        """获取 JSON Schema"""
        schema = get_json_schema_guide()
        return [TextContent(type="text", text=schema)]

    async def _generate_character_reference(
        self,
        character_name: str,
        description: str,
        visual_features: Optional[Dict] = None,
        style: str = "日漫风格"
    ) -> list[TextContent]:
        """生成人物参考图"""
        logger.info(f"🎨 生成人物参考图: {character_name}")

        character = await self.character_manager.create_character(
            name=character_name,
            description=description,
            visual_features=visual_features,
            style=style
        )

        result = {
            "success": True,
            "character_id": character.character_id,
            "name": character.name,
            "message": f"人物参考图已生成并保存到 {character.reference_image.path}",
            "visual_features": character.visual_features.model_dump(),
            "next_step": f"在 JSON 中使用 character_name: '{character_name}' 来引用这个角色"
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]

    async def _generate_scene_reference(
        self,
        scene_name: str,
        description: str,
        tags: Optional[List[str]] = None,
        style: str = "日漫风格"
    ) -> list[TextContent]:
        """生成场景参考图"""
        logger.info(f"🎨 生成场景参考图: {scene_name}")

        scene = await self.scene_manager.create_scene(
            name=scene_name,
            description=description,
            tags=tags,
            style=style
        )

        result = {
            "success": True,
            "scene_id": scene.scene_id,
            "name": scene.name,
            "message": f"场景参考图已生成并保存到 {scene.reference_image.path}",
            "tags": scene.tags,
            "next_step": f"在 JSON 的 background 字段中使用 '{scene_name}' 来引用这个场景"
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]

    async def _generate_comic_page(
        self,
        json_path: str,
        image_size: str = "4K",
        aspect_ratio: str = "3:4",
        style: str = "日漫风格"
    ) -> list[TextContent]:
        """生成漫画图片（核心工具）"""
        try:
            # 从文件读取 JSON
            json_file = Path(json_path)
            if not json_file.exists():
                # 尝试相对于项目根目录的路径
                project_root = Path(__file__).parent.parent
                json_file = project_root / json_path

            if not json_file.exists():
                raise FileNotFoundError(f"找不到 JSON 文件: {json_path}")

            logger.info(f"📂 从文件读取 JSON: {json_file}")

            with open(json_file, 'r', encoding='utf-8') as f:
                page_json = f.read()

            # 尝试修复并解析 JSON
            page_data = self._fix_and_parse_json(page_json)
            page = Page(**page_data)

            logger.info(f"📄 生成第 {page.page_number} 页，共 {len(page.panels)} 个分镜")

            # 调用核心生成逻辑
            return await self._generate_comic_page_logic(
                page=page,
                image_size=image_size,
                aspect_ratio=aspect_ratio,
                style=style
            )

        except FileNotFoundError as e:
            raise ValueError(str(e))
        except ValueError as e:
            # JSON 解析或修复失败
            raise e
        except Exception as e:
            logger.error(f"生成失败: {e}")
            raise

    async def _list_characters(self) -> list[TextContent]:
        """列出所有人物"""
        characters = self.character_manager.list_characters()

        result = [
            {
                "character_id": c.character_id,
                "name": c.name,
                "description": c.description,
                "visual_features": c.visual_features.model_dump(),
                "usage_count": c.metadata.usage_count,
                "reference_image": c.reference_image.path
            }
            for c in characters
        ]

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]

    async def _list_scenes(self) -> list[TextContent]:
        """列出所有场景"""
        scenes = self.scene_manager.list_scenes()

        result = [
            {
                "scene_id": s.scene_id,
                "name": s.name,
                "description": s.description,
                "tags": s.tags,
                "usage_count": s.metadata.usage_count,
                "reference_image": s.reference_image.path
            }
            for s in scenes
        ]

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]

    async def _update_character_reference(
        self,
        character_id: str,
        new_description: str
    ) -> list[TextContent]:
        """更新人物参考图"""
        character = await self.character_manager.update_character_reference(
            character_id=character_id,
            new_description=new_description
        )

        if not character:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"角色不存在: {character_id}"
                }, ensure_ascii=False)
            )]

        result = {
            "success": True,
            "character_id": character.character_id,
            "name": character.name,
            "message": f"参考图已更新: {character.reference_image.path}"
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]

    async def _regenerate_page(
        self,
        json_path: str,
        image_size: str = "4K",
        aspect_ratio: str = "3:4",
        style: str = "日漫风格"
    ) -> list[TextContent]:
        """重新生成指定页面"""
        try:
            # 从文件读取 JSON
            json_file = Path(json_path)
            if not json_file.exists():
                # 尝试相对于项目根目录的路径
                project_root = Path(__file__).parent.parent
                json_file = project_root / json_path

            if not json_file.exists():
                raise FileNotFoundError(f"找不到 JSON 文件: {json_path}")

            logger.info(f"📂 从文件读取 JSON: {json_file}")

            with open(json_file, 'r', encoding='utf-8') as f:
                page_json = f.read()

            # 尝试修复并解析 JSON
            page_data = self._fix_and_parse_json(page_json)
            page = Page(**page_data)

            logger.info(f"🔄 重新生成第 {page.page_number} 页，共 {len(page.panels)} 个分镜")

            # 调用生成页面的逻辑
            result = await self._generate_comic_page_logic(
                page=page,
                image_size=image_size,
                aspect_ratio=aspect_ratio,
                style=style
            )

            # 添加重新生成的标记
            result_dict = json.loads(result[0].text)
            result_dict["regenerated"] = True
            result_dict["message"] = f"✅ 第 {page.page_number} 页已重新生成（覆盖原文件）！"

            return [TextContent(
                type="text",
                text=json.dumps(result_dict, ensure_ascii=False, indent=2)
            )]

        except FileNotFoundError as e:
            raise ValueError(str(e))
        except ValueError as e:
            # JSON 解析或修复失败
            raise e
        except Exception as e:
            logger.error(f"重新生成失败: {e}")
            raise

    def _fix_and_parse_json(self, page_json: str) -> dict:
        """尝试修复并解析 JSON，返回解析后的数据"""
        import re

        # 首次尝试直接解析
        try:
            return json.loads(page_json)
        except json.JSONDecodeError as e:
            error_msg = str(e)
            logger.warning(f"⚠️  JSON 解析失败，尝试自动修复: {error_msg}")

            # 尝试修复：移除尾随逗号
            if "Expecting value" in error_msg:
                fixed_json = re.sub(r',\s*([}\]])', r'\1', page_json)
                try:
                    data = json.loads(fixed_json)
                    logger.info("✅ 已自动修复: 移除了多余的逗号")
                    return data
                except:
                    logger.warning("移除尾随逗号修复失败")

            # 尝试修复：处理未转义的引号（简单情况）
            # 这里不做复杂的引号修复，因为容易出错
            # 如果真的有引号问题，直接抛出原始错误

            # 所有修复尝试失败，抛出原始错误
            raise ValueError(f"JSON 格式错误且无法自动修复: {error_msg}")

    async def _generate_comic_page_logic(
        self,
        page: Page,
        image_size: str,
        aspect_ratio: str,
        style: str
    ) -> list[TextContent]:
        """生成漫画页面的核心逻辑（被 generate_comic_page 和 regenerate_page 共享）"""
        # 收集所有角色和场景
        all_character_names = set()
        all_scene_names = set()

        for panel in page.panels:
            for char in panel.characters:
                all_character_names.add(char.name)
            if panel.background:
                all_scene_names.add(panel.background)

        # 确保所有角色都有参考图
        character_refs = []
        for char_name in all_character_names:
            char = self.character_manager.get_character_by_name(char_name)
            if not char:
                # 自动创建角色参考图
                logger.warning(f"⚠️  角色 '{char_name}' 没有参考图，自动创建")
                char = await self.character_manager.create_character(
                    name=char_name,
                    description=f"角色 {char_name}",
                    style=style
                )
            character_refs.append(char.reference_image.base64)

        # 收集已有的场景参考图（不自动创建）
        scene_refs = []
        for scene_name in all_scene_names:
            scene = self.scene_manager.get_scene_by_name(scene_name)
            if scene:
                scene_refs.append(scene.reference_image.base64)
            else:
                logger.info(f"ℹ️  场景 '{scene_name}' 没有参考图，跳过（不自动生成）")

        # 生成图片（所有分镜合并为一张图）
        all_descriptions = []
        for panel in page.panels:
            desc = f"分镜{panel.panel_number}: {panel.description}"
            if panel.camera_angle:
                desc = f"{panel.camera_angle}镜头。{desc}"
            # 如果有对话，添加到描述中，并强调使用中文
            if panel.dialogues:
                dialogue_text = "，对话："
                for d in panel.dialogues:
                    dialogue_text += f"{d.speaker}说（用中文）：'{d.text}' "
                desc += dialogue_text
            # 如果有音效，添加到描述中
            if panel.sound_effects:
                desc += f"，音效文字（用中文显示）：{' '.join(panel.sound_effects)}"
            all_descriptions.append(desc)

        full_description = f"{style}风格的漫画页面，包含 {len(page.panels)} 个分镜。\n"
        full_description += "重要要求：\n"
        full_description += "1. 所有对话、字幕、音效文字必须使用中文显示\n"
        full_description += "2. 字幕和对话气泡的排版必须遵循现代阅读习惯：从左往右、从下往上排列\n"
        full_description += "\n".join(all_descriptions)

        # 调用 Gemini API 生成图片
        logger.info(f"🎨 调用 Gemini API 生成图片...")
        all_refs = character_refs + scene_refs

        image_base64 = await self.gemini_client.generate_with_references(
            prompt=full_description,
            image_refs=all_refs if all_refs else None,
            image_size=image_size,
            aspect_ratio=aspect_ratio
        )

        # 保存图片
        output_dir = Path(self.config.get("storage", {}).get("output_images_path", "./output/pages"))
        output_path = output_dir / f"page_{page.page_number:03d}.jpg"
        self.gemini_client.save_base64_image(image_base64, output_path)

        result = {
            "success": True,
            "page_number": page.page_number,
            "panels_count": len(page.panels),
            "image_path": str(output_path),
            "characters_used": list(all_character_names),
            "scenes_used": list(all_scene_names),
            "message": f"✅ 第 {page.page_number} 页漫画已生成！"
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]


async def main():
    """启动 MCP 服务器"""
    server_instance = ComicMCPServer()

    # 启动服务器
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="comic-service",
                server_version="0.2.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
