"""
人物参考图管理
管理人物参考图的生成、存储、加载
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from loguru import logger

from ..models.character import Character, VisualFeatures, ReferenceImage, CharacterMetadata
from .gemini_client import GeminiImageGenerator


class CharacterManager:
    """人物参考图管理器"""

    def __init__(
        self,
        gemini_client: GeminiImageGenerator,
        storage_dir: Path = Path("./config/references/characters")
    ):
        """
        初始化人物管理器

        Args:
            gemini_client: Gemini API 客户端
            storage_dir: 存储目录
        """
        self.gemini_client = gemini_client
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.characters: Dict[str, Character] = {}
        self._load_all_characters()

    def _load_all_characters(self):
        """加载所有已保存的人物"""
        if not self.storage_dir.exists():
            return

        for json_file in self.storage_dir.glob("*.json"):
            try:
                character = Character.load_from_file(json_file)
                self.characters[character.character_id] = character
                logger.info(f"加载人物: {character.name} ({character.character_id})")
            except Exception as e:
                logger.warning(f"加载人物文件失败 {json_file}: {e}")

    async def create_character(
        self,
        name: str,
        description: str,
        visual_features: Optional[Dict] = None,
        style: str = "日漫风格",
        reference_image: Optional[str] = None
    ) -> Character:
        """
        创建新人物并生成参考图

        Args:
            name: 角色名称
            description: 角色描述
            visual_features: 视觉特征（可选）
            style: 漫画风格
            reference_image: 参考图片的本地路径（可选）

        Returns:
            创建的角色对象
        """
        # 生成角色 ID
        character_id = f"char_{name.lower().replace(' ', '_')}"

        # 生成参考图
        logger.info(f"正在生成人物参考图: {name}")
        image_base64 = await self.gemini_client.generate_character_reference(
            character_name=name,
            description=description,
            style=style,
            reference_image=reference_image
        )

        # 压缩图片 base64（用于 API 调用）
        compressed_base64 = self.gemini_client.compress_base64_image(image_base64)

        # 保存图片（会自动压缩）
        image_path = self.storage_dir / f"{character_id}.jpg"
        self.gemini_client.save_base64_image(image_base64, image_path, compress=True)

        # 创建视觉特征
        if visual_features is None:
            visual_features = {
                "hair_color": "未指定",
                "clothing": "根据描述自动生成",
                "age_range": "未指定"
            }

        # 创建角色对象
        character = Character(
            character_id=character_id,
            name=name,
            description=description,
            reference_image=ReferenceImage(
                base64=compressed_base64,
                path=str(image_path),
                model_used=self.gemini_client.model
            ),
            visual_features=VisualFeatures(**visual_features),
            metadata=CharacterMetadata()
        )

        # 保存到内存和文件
        self.characters[character_id] = character
        character.save_to_file(self.storage_dir)

        logger.success(f"人物创建成功: {name} ({character_id})")
        return character

    def get_character(self, character_id: str) -> Optional[Character]:
        """获取角色"""
        return self.characters.get(character_id)

    def get_character_by_name(self, name: str) -> Optional[Character]:
        """通过名称获取角色"""
        for character in self.characters.values():
            if character.name == name:
                return character
        return None

    def list_characters(self) -> List[Character]:
        """列出所有角色"""
        return list(self.characters.values())

    def get_character_refs_base64(self, character_ids: List[str]) -> List[str]:
        """
        获取角色的参考图 base64 列表

        Args:
            character_ids: 角色 ID 列表

        Returns:
            base64 编码的图片列表
        """
        refs = []
        for char_id in character_ids:
            character = self.get_character(char_id)
            if character:
                refs.append(character.reference_image.base64)
                character.update_usage()
        return refs

    async def update_character_reference(
        self,
        character_id: str,
        new_description: Optional[str] = None
    ) -> Optional[Character]:
        """
        更新人物参考图

        Args:
            character_id: 角色 ID
            new_description: 新描述（可选）

        Returns:
            更新后的角色对象
        """
        character = self.get_character(character_id)
        if not character:
            logger.error(f"角色不存在: {character_id}")
            return None

        # 使用新描述或原描述
        description = new_description or character.description

        # 重新生成参考图
        logger.info(f"正在更新人物参考图: {character.name}")
        image_base64 = await self.gemini_client.generate_character_reference(
            character_name=character.name,
            description=description
        )

        # 压缩图片 base64
        compressed_base64 = self.gemini_client.compress_base64_image(image_base64)

        # 更新图片（会自动压缩）
        image_path = self.storage_dir / f"{character_id}.jpg"
        self.gemini_client.save_base64_image(image_base64, image_path, compress=True)

        # 更新角色对象
        character.reference_image = ReferenceImage(
            base64=compressed_base64,
            path=str(image_path),
            model_used=self.gemini_client.model
        )

        if new_description:
            character.description = new_description

        character.metadata.updated_at = character.metadata.updated_at

        # 保存更新
        character.save_to_file(self.storage_dir)

        logger.success(f"人物参考图更新成功: {character.name}")
        return character

    def delete_character(self, character_id: str) -> bool:
        """删除角色"""
        if character_id not in self.characters:
            logger.warning(f"角色不存在: {character_id}")
            return False

        del self.characters[character_id]

        # 删除文件
        json_file = self.storage_dir / f"{character_id}.json"
        image_file = self.storage_dir / f"{character_id}.jpg"

        if json_file.exists():
            json_file.unlink()
        if image_file.exists():
            image_file.unlink()

        logger.info(f"角色已删除: {character_id}")
        return True
