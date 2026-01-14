"""
人物数据模型
定义漫画角色的数据结构和参考图管理
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from pathlib import Path


class VisualFeatures(BaseModel):
    """人物视觉特征"""
    hair_color: str = Field(description="发色")
    hair_style: Optional[str] = Field(None, description="发型")
    clothing: str = Field(description="服装")
    accessories: Optional[str] = Field(None, description="配饰")
    age_range: Optional[str] = Field(None, description="年龄范围，如 20-25")
    facial_features: Optional[str] = Field(None, description="面部特征")
    body_type: Optional[str] = Field(None, description="体型")


class ReferenceImage(BaseModel):
    """参考图数据"""
    base64: str = Field(description="base64 编码的图片数据")
    path: str = Field(description="图片存储路径")
    generated_at: datetime = Field(default_factory=datetime.now, description="生成时间")
    model_used: str = Field(description="使用的模型")


class CharacterMetadata(BaseModel):
    """人物元数据"""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    usage_count: int = Field(default=0, description="使用次数")


class Character(BaseModel):
    """漫画角色模型"""
    character_id: str = Field(description="角色唯一标识，如 char_liubei")
    name: str = Field(description="角色名称")
    description: str = Field(description="角色描述")
    reference_image: ReferenceImage = Field(description="参考图")
    visual_features: VisualFeatures = Field(description="视觉特征")
    metadata: CharacterMetadata = Field(default_factory=CharacterMetadata)

    def update_usage(self):
        """更新使用次数"""
        self.metadata.usage_count += 1
        self.metadata.updated_at = datetime.now()

    def save_to_file(self, directory: Path):
        """保存角色数据到文件"""
        import json

        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / f"{self.character_id}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(
                self.model_dump(mode='json'),
                f,
                ensure_ascii=False,
                indent=2,
                default=str
            )

        return file_path

    @classmethod
    def load_from_file(cls, file_path: Path) -> 'Character':
        """从文件加载角色数据"""
        import json

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return cls(**data)


class Scene(BaseModel):
    """场景模型"""
    scene_id: str = Field(description="场景唯一标识，如 scene_street")
    name: str = Field(description="场景名称")
    description: str = Field(description="场景描述")
    reference_image: ReferenceImage = Field(description="参考图")
    tags: list[str] = Field(default_factory=list, description="场景标签")
    metadata: CharacterMetadata = Field(default_factory=CharacterMetadata)

    def update_usage(self):
        """更新使用次数"""
        self.metadata.usage_count += 1
        self.metadata.updated_at = datetime.now()

    def save_to_file(self, directory: Path):
        """保存场景数据到文件"""
        import json

        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / f"{self.scene_id}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(
                self.model_dump(mode='json'),
                f,
                ensure_ascii=False,
                indent=2,
                default=str
            )

        return file_path

    @classmethod
    def load_from_file(cls, file_path: Path) -> 'Scene':
        """从文件加载场景数据"""
        import json

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return cls(**data)
