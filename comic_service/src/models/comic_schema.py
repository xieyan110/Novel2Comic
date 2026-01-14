"""
漫画数据模型
定义漫画分镜、页面等数据结构
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Dialogue(BaseModel):
    """对话"""
    speaker: str = Field(description="说话人角色名")
    text: str = Field(description="对话内容")
    position: Optional[Dict[str, float]] = Field(None, description="气泡位置 {x, y, width, height}")
    emotion: Optional[str] = Field(None, description="情绪，如：愤怒、悲伤、喜悦")


class CharacterPosition(BaseModel):
    """角色位置"""
    name: str = Field(description="角色名称")
    action: Optional[str] = Field(None, description="动作描述")
    expression: Optional[str] = Field(None, description="表情")
    position_hint: Optional[str] = Field(None, description="位置提示（左侧、右侧、中间、前景、背景等）")


class Panel(BaseModel):
    """分镜格"""
    model_config = {"extra": "ignore"}
    panel_number: int = Field(description="格子编号")
    characters: List[CharacterPosition] = Field(default_factory=list, description="出场角色及位置")
    dialogues: List[Dialogue] = Field(default_factory=list, description="对话内容")
    background: str = Field(description="背景场景描述")
    background_ref: Optional[str] = Field(None, description="背景参考图ID")
    camera_angle: str = Field(description="镜头角度，如：全景、特写、俯视")
    sound_effects: Optional[List[str]] = Field(None, description="音效文字")
    description: str = Field(description="画面描述")
    layout: Optional[Dict[str, Any]] = Field(None, description="布局信息")


class Page(BaseModel):
    """漫画页"""
    page_number: int = Field(description="页码")
    panels: List[Panel] = Field(default_factory=list, description="分镜格数组")
    page_notes: Optional[str] = Field(None, description="页面备注")
    layout_type: Optional[str] = Field(None, description="页面布局类型")


class ProjectOverview(BaseModel):
    """项目总览"""
    project_name: str = Field(description="项目名称")
    estimated_pages: int = Field(description="预计页数")
    characters: List[Dict[str, str]] = Field(default_factory=list, description="角色列表 [{name, description}]")
    scenes: List[Dict[str, str]] = Field(default_factory=list, description="场景列表 [{name, description}]")
    chapters: List[Dict[str, Any]] = Field(default_factory=list, description="章节列表")
    style: Optional[str] = Field(None, description="漫画风格")
    summary: Optional[str] = Field(None, description="故事摘要")


class ComicProject(BaseModel):
    """完整漫画项目"""
    overview: ProjectOverview = Field(description="项目总览")
    pages: List[Page] = Field(default_factory=list, description="所有页面")
    characters: Dict[str, Any] = Field(default_factory=dict, description="角色数据")
    scenes: Dict[str, Any] = Field(default_factory=dict, description="场景数据")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="项目元数据")

    def add_page(self, page: Page):
        """添加页面"""
        self.pages.append(page)

    def get_page(self, page_number: int) -> Optional[Page]:
        """获取指定页面"""
        for page in self.pages:
            if page.page_number == page_number:
                return page
        return None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.model_dump(mode='json')
