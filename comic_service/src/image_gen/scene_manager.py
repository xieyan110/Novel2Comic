"""
场景参考图管理
管理场景参考图的生成、存储、加载
"""

from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger

from ..models.character import Scene, CharacterMetadata
from .gemini_client import GeminiImageGenerator


class SceneManager:
    """场景参考图管理器"""

    def __init__(
        self,
        gemini_client: GeminiImageGenerator,
        storage_dir: Path = Path("./config/references/scenes")
    ):
        """
        初始化场景管理器

        Args:
            gemini_client: Gemini API 客户端
            storage_dir: 存储目录
        """
        self.gemini_client = gemini_client
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.scenes: Dict[str, Scene] = {}
        self._load_all_scenes()

    def _load_all_scenes(self):
        """加载所有已保存的场景"""
        if not self.storage_dir.exists():
            return

        for json_file in self.storage_dir.glob("*.json"):
            try:
                scene = Scene.load_from_file(json_file)
                self.scenes[scene.scene_id] = scene
                logger.info(f"加载场景: {scene.name} ({scene.scene_id})")
            except Exception as e:
                logger.warning(f"加载场景文件失败 {json_file}: {e}")

    async def create_scene(
        self,
        name: str,
        description: str,
        tags: Optional[List[str]] = None,
        style: str = "日漫风格"
    ) -> Scene:
        """
        创建新场景并生成参考图

        Args:
            name: 场景名称
            description: 场景描述
            tags: 场景标签
            style: 漫画风格

        Returns:
            创建的场景对象
        """
        # 生成场景 ID
        scene_id = f"scene_{name.lower().replace(' ', '_')}"

        # 生成参考图
        logger.info(f"正在生成场景参考图: {name}")
        image_base64 = await self.gemini_client.generate_scene_reference(
            scene_name=name,
            description=description,
            style=style
        )

        # 压缩图片 base64
        compressed_base64 = self.gemini_client.compress_base64_image(image_base64)

        # 保存图片（会自动压缩）
        image_path = self.storage_dir / f"{scene_id}.jpg"
        self.gemini_client.save_base64_image(image_base64, image_path, compress=True)

        # 创建场景对象
        scene = Scene(
            scene_id=scene_id,
            name=name,
            description=description,
            reference_image={
                "base64": compressed_base64,
                "path": str(image_path),
                "model_used": self.gemini_client.model
            },
            tags=tags or [],
            metadata=CharacterMetadata()
        )

        # 保存到内存和文件
        self.scenes[scene_id] = scene
        scene.save_to_file(self.storage_dir)

        logger.success(f"场景创建成功: {name} ({scene_id})")
        return scene

    def get_scene(self, scene_id: str) -> Optional[Scene]:
        """获取场景"""
        return self.scenes.get(scene_id)

    def get_scene_by_name(self, name: str) -> Optional[Scene]:
        """通过名称获取场景"""
        for scene in self.scenes.values():
            if scene.name == name:
                return scene
        return None

    def list_scenes(self) -> List[Scene]:
        """列出所有场景"""
        return list(self.scenes.values())

    def get_scene_refs_base64(self, scene_ids: List[str]) -> List[str]:
        """
        获取场景的参考图 base64 列表

        Args:
            scene_ids: 场景 ID 列表

        Returns:
            base64 编码的图片列表
        """
        refs = []
        for scene_id in scene_ids:
            scene = self.get_scene(scene_id)
            if scene:
                refs.append(scene.reference_image.base64)
                scene.update_usage()
        return refs

    async def update_scene_reference(
        self,
        scene_id: str,
        new_description: Optional[str] = None
    ) -> Optional[Scene]:
        """
        更新场景参考图

        Args:
            scene_id: 场景 ID
            new_description: 新描述（可选）

        Returns:
            更新后的场景对象
        """
        scene = self.get_scene(scene_id)
        if not scene:
            logger.error(f"场景不存在: {scene_id}")
            return None

        # 使用新描述或原描述
        description = new_description or scene.description

        # 重新生成参考图
        logger.info(f"正在更新场景参考图: {scene.name}")
        image_base64 = await self.gemini_client.generate_scene_reference(
            scene_name=scene.name,
            description=description
        )

        # 压缩图片 base64
        compressed_base64 = self.gemini_client.compress_base64_image(image_base64)

        # 更新图片（会自动压缩）
        image_path = self.storage_dir / f"{scene_id}.jpg"
        self.gemini_client.save_base64_image(image_base64, image_path, compress=True)

        # 更新场景对象
        from ..models.character import ReferenceImage
        scene.reference_image = ReferenceImage(
            base64=compressed_base64,
            path=str(image_path),
            model_used=self.gemini_client.model
        )

        if new_description:
            scene.description = new_description

        scene.metadata.updated_at = scene.metadata.updated_at

        # 保存更新
        scene.save_to_file(self.storage_dir)

        logger.success(f"场景参考图更新成功: {scene.name}")
        return scene

    def delete_scene(self, scene_id: str) -> bool:
        """删除场景"""
        if scene_id not in self.scenes:
            logger.warning(f"场景不存在: {scene_id}")
            return False

        del self.scenes[scene_id]

        # 删除文件
        json_file = self.storage_dir / f"{scene_id}.json"
        image_file = self.storage_dir / f"{scene_id}.jpg"

        if json_file.exists():
            json_file.unlink()
        if image_file.exists():
            image_file.unlink()

        logger.info(f"场景已删除: {scene_id}")
        return True
