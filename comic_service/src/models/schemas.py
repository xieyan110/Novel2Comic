"""
JSON Schema 定义
提供给 AI 工具的 JSON 格式模板
"""

import json

# 漫画页面 JSON Schema
COMIC_PAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "page_number": {
            "type": "integer",
            "description": "页码"
        },
        "panels": {
            "type": "array",
            "description": "分镜格数组",
            "items": {
                "type": "object",
                "properties": {
                    "panel_number": {
                        "type": "integer",
                        "description": "格子编号（从1开始）"
                    },
                    "description": {
                        "type": "string",
                        "description": "画面描述，用于生成图片。必须详细、具体"
                    },
                    "characters": {
                        "type": "array",
                        "description": "出场角色",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "角色名称"
                                },
                                "action": {
                                    "type": "string",
                                    "description": "动作描述（站立、坐着、行走等）"
                                },
                                "expression": {
                                    "type": "string",
                                    "description": "表情（微笑、愤怒、悲伤等）"
                                },
                                "position_hint": {
                                    "type": "string",
                                    "description": "位置提示（左侧、右侧、中间、前景、背景等）"
                                }
                            },
                            "required": ["name"]
                        }
                    },
                    "dialogues": {
                        "type": "array",
                        "description": "对话内容",
                        "items": {
                            "type": "object",
                            "properties": {
                                "speaker": {
                                    "type": "string",
                                    "description": "说话人角色名"
                                },
                                "text": {
                                    "type": "string",
                                    "description": "对话内容"
                                },
                                "emotion": {
                                    "type": "string",
                                    "description": "情绪（愤怒、悲伤、喜悦、惊讶等）"
                                },
                                "position": {
                                    "type": "object",
                                    "description": "气泡位置 {x, y, width, height}",
                                    "properties": {
                                        "x": {"type": "number", "description": "X坐标"},
                                        "y": {"type": "number", "description": "Y坐标"},
                                        "width": {"type": "number", "description": "宽度"},
                                        "height": {"type": "number", "description": "高度"}
                                    }
                                }
                            },
                            "required": ["speaker", "text"]
                        }
                    },
                    "background": {
                        "type": "string",
                        "description": "背景场景描述"
                    },
                    "camera_angle": {
                        "type": "string",
                        "description": "镜头角度（全景、中景、特写、俯视、仰视等）",
                        "enum": ["全景", "远景", "中景", "特写", "大特写", "俯视", "仰视", "平视", "鸟瞰"]
                    },
                    "sound_effects": {
                        "type": "array",
                        "description": "音效文字（可选）",
                        "items": {"type": "string"}
                    },
                    "layout": {
                        "type": "object",
                        "description": "布局信息（可选）",
                        "properties": {}
                    }
                },
                "required": ["panel_number", "description"]
            }
        }
    },
    "required": ["page_number", "panels"],
    "page_notes": {
        "type": "string",
        "description": "页面备注（可选）"
    },
    "layout_type": {
        "type": "string",
        "description": "页面布局类型（可选）"
    }
}

# JSON Schema 示例（供 AI 参考）
# 注意：每个 JSON 只包含一个 panel（一个分镜格）
COMIC_PAGE_EXAMPLE = {
    "page_number": 1,
    "panels": [
        {
            "panel_number": 1,
            "description": "全景镜头。现代城市街道，阳光明媚。一个十岁男孩（小明）走在人行道上，两侧是绿树和建筑物。日漫风格，色彩明亮。",
            "characters": [
                {
                    "name": "小明",
                    "action": "行走",
                    "expression": "轻松",
                    "position_hint": "画面中央，略微偏左"
                }
            ],
            "dialogues": [],
            "background": "现代城市街道",
            "camera_angle": "全景"
        }
    ]
}

# 更多示例（每个示例都是一个独立的 JSON/格子）
COMIC_PANEL_EXAMPLES = [
    {
        "page_number": 1,
        "panels": [{
            "panel_number": 1,
            "description": "全景镜头。现代城市街道，阳光明媚。一个十岁男孩（小明）走在人行道上，两侧是绿树和建筑物。日漫风格，色彩明亮。",
            "characters": [{"name": "小明", "action": "行走", "expression": "轻松", "position_hint": "画面中央"}],
            "dialogues": [],
            "background": "现代城市街道",
            "camera_angle": "全景"
        }]
    },
    {
        "page_number": 2,
        "panels": [{
            "panel_number": 1,
            "description": "中景镜头。小明蹲下身，微笑着伸出右手。前方有一只橘色小猫，毛茸茸的，正抬头看着他。背景是街道，虚化处理。",
            "characters": [{"name": "小明", "action": "蹲下，伸手", "expression": "温柔微笑", "position_hint": "画面左侧"}],
            "dialogues": [{"speaker": "小明", "text": "你好啊，小家伙！", "emotion": "喜悦"}],
            "background": "街道背景",
            "camera_angle": "中景"
        }]
    },
    {
        "page_number": 3,
        "panels": [{
            "panel_number": 1,
            "description": "小猫背对着镜头跑开，只留下尾巴的剪影。小明站在原地，表情惊讶，双手张开。背景是街道，有几片落叶飘下。",
            "characters": [{"name": "小明", "action": "站立，双手张开", "expression": "惊讶", "position_hint": "画面右侧"}],
            "dialogues": [],
            "background": "街道",
            "camera_angle": "中景",
            "sound_effects": ["喵~"]
        }]
    }
]

# 获取完整的工作流程指引
def get_workflow_guide() -> str:
    """获取工作流程指引"""
    return """# 漫画生成工作流程

当用户要求将小说转换为漫画时，请按以下步骤操作：

## 📌 重要提醒：查看 JSON Schema

**在开始之前，请务必调用 `get_json_schema` 工具查看完整的 JSON Schema 和示例！**

这将帮助您：
- 了解正确的 JSON 格式
- 查看完整的字段列表和说明
- 参考实际的 JSON 示例

## 核心概念：根据漫画风格组织分镜

**不同漫画风格有不同的分镜布局：**

### 🇯🇵 日式漫画（Manga）
- **特点：一页包含 4-8 个分镜格**，紧凑布局
- **布局方式**：一个 JSON 的 `panels` 数组包含多个格子
- **视觉风格**：格子大小不一，有的格子跨栏，强调节奏感

### 🇨🇳 中式漫画 / 🇰🇷 韩式漫画（Manhwa）
- **特点：一页包含 1-3 个分镜格**，宽松布局
- **布局方式**：一个 JSON 的 `panels` 数组包含少量格子
- **视觉风格**：格子较大，画面完整，强调细节

**重要：**
- 一个 JSON = 一页漫画（包含多个或单个格子）
- `panels` 数组中的元素数量由漫画风格决定

## 分镜示例对比

**相同故事：**"小明走在街上。看到了一只小猫。他说：你好小猫。小猫跑了。"

### 日式漫画分镜（紧凑，一页多格）
```
第1页 JSON (包含 4 个格子):
- 格1: "小明悠闲地走在街道上（全景）"
- 格2: "小明停下脚步，发现地上的小猫（中景）"
- 格3: "小猫蹲在路边，可爱地看着前方（特写）"
- 格4: "小明蹲下身，温柔地伸出手（近景）"

第2页 JSON (包含 4 个格子):
- 格1: "小明微笑着说：你好小猫（对话特写）"
- 格2: "小猫突然受惊，耳朵竖起（特写）"
- 格3: "小猫转身跑开，动态模糊（动作）"
- 格4: "小猫跑远的背影，小明伸手挽留（远景）"
```

### 中式/韩式漫画分镜（宽松，一页少格）
```
第1页 JSON (包含 2 个格子):
- 格1: "小明走在街道上，看到路边的小猫（全景）"
- 格2: "小明蹲下身，温柔地伸出手与小猫互动（中景）"

第2页 JSON (包含 2 个格子):
- 格1: "小明微笑着对猫说话，小猫好奇地看着（近景）"
- 格2: "小猫突然转身跑开，小明表情惊讶（全景）"
```

## 第一步：分析文本

1. **识别所有出场角色** - 列出小说中出现的所有人物
2. **识别主要场景** - 列出小说中出现的地点/场景

## 第二步：询问用户配置

必须向用户询问以下配置选项：

### 1️⃣ 分辨率选择
- **1K** - 文字会糊掉，仅用于快速预览
- **2K** - 平衡画质和生成速度
- **4K** - 最高画质，文字清晰（推荐）

### 2️⃣ 漫画风格选择
- **日式漫画（日漫风格）** - 紧凑布局，每页 4-8 个格子，快节奏
- **中式漫画（国风/中式风格）** - 宽松布局，每页 1-3 个格子，强调细节
- **韩式漫画（韩式风格）** - 宽松布局，每页 1-3 个格子，强调细节
- **其他风格（5个分镜彩色）** - 固定 5 个分镜格搭配3个分镜的用于特写，彩色漫画风格

### 3️⃣ 奇数格偏好（可选）
- **是否尽可能使用奇数格**：1、3、5、7 个格子
  - 优点：构图更平衡，视觉重心突出
  - 缺点：可能需要在分镜设计上做额外调整

## 第三步：检查并生成角色参考图

调用 `list_characters` 工具检查当前已有的角色参考图。

### 可能的情况及处理方式：

#### 情况 A：一个都没有
- 对文本中识别出的**所有角色**，调用 `generate_character_reference` 生成参考图
- 参数：
  - `character_name`: 角色名称
  - `description`: 详细的外貌描述（发色、发型、服装、年龄、体型等）
  - `visual_features`: 视觉特征（可选，JSON 格式）
  - `style`: 漫画风格

#### 情况 B：全有
- 检查现有角色是否与文本中的角色匹配
- 如果匹配，跳过此步骤
- 如果有新角色，只为新角色生成参考图

#### 情况 C：只有部分
- 对比已有角色和文本中的角色
- 只为**缺失的角色**生成参考图

## 第四步：检查并生成场景参考图

调用 `list_scenes` 工具检查当前已有的场景参考图。

### 处理方式：
- 识别文本中的**关键场景**（重要地点、反复出现的场景）
- 检查这些场景是否已有参考图
- 对缺失的场景，调用 `generate_scene_reference` 生成参考图
  - `scene_name`: 场景名称
  - `description`: 详细的场景描述（环境、光线、氛围等）
  - `tags`: 场景标签（可选，如：城市、街道、白天等）
  - `style`: 漫画风格

## 第五步：生成 JSON

注意生成json 之前记得 先调用 get_json_schema 查看格式

根据用户选择的漫画风格，为每一页生成一个 JSON 文件。

### 日式漫画 JSON 示例（一页多格）
```json
{
  "page_number": 1,
  "panels": [
    {"panel_number": 1, "description": "全景...", "camera_angle": "全景"},
    {"panel_number": 2, "description": "中景...", "camera_angle": "中景"},
    {"panel_number": 3, "description": "特写...", "camera_angle": "特写"},
    {"panel_number": 4, "description": "近景...", "camera_angle": "近景"}
  ]
}
```

### 中式/韩式漫画 JSON 示例（一页少格）
```json
{
  "page_number": 1,
  "panels": [
    {"panel_number": 1, "description": "全景...", "camera_angle": "全景"}
  ]
}
```

**将每个 JSON 保存为文件**（如 `page_001.json`、`page_002.json` 等）

### ⚠️ JSON 格式重要提示

生成 JSON 时请注意以下**关键格式要求**：

1. **对话中的引号必须转义**
   ```json
   ❌ "text": "他说: "你好""
   ✅ "text": "他说: \"你好\""
   ```

2. **不要在数组最后一个元素后加逗号**
   ```json
   ❌ "panels": [{...}, {...},]
   ✅ "panels": [{...}, {...}]
   ```

3. **确保所有引号和括号匹配**
   - 检查每个 `{` 都有对应的 `}`
   - 检查每个 `[` 都有对应的 `]`
   - 检查双引号成对出现

4. **使用标准 JSON 格式**
   - 键名必须用双引号包围
   - 字符串值必须用双引号包围
   - 不能使用单引号
   - 不能有注释（// 或 /* */）

MCP 服务会自动修复常见的 JSON 错误（如多余逗号），但复杂的格式问题仍会导致生成失败。

## 第六步：逐页生成漫画

对每个 JSON 文件，调用 `generate_comic_page` 工具：
- `json_path`: JSON 文件路径（相对于项目根目录，如 `output/page_001.json`）
- `image_size`: 用户选择的图片大小（1K/2K/4K）
- `aspect_ratio`: 长宽比（默认 3:4）
- `style`: 用户选择的漫画风格（"日漫风格" / "中式漫画风格" / "韩式漫画风格"）

MCP 服务会：
1. 从文件读取 JSON
2. 自动尝试修复常见的 JSON 格式错误
3. 为所有角色和场景准备参考图
4. 调用 Gemini API 生成漫画页
5. 返回图片地址

## 重要提示
- **第二步询问是必需的** - 必须明确用户需要的分辨率、风格和奇数格偏好
- **第三、四步检查是关键** - 避免重复生成已有的参考图，节省时间和成本
- **description 字段必须详细具体**，包含所有视觉元素
- 保持角色视觉一致性（使用相同的角色参考图）
- **MCP 服务会自动修复常见的 JSON 格式错误**（如多余逗号等）

"""

# 获取 JSON Schema 说明
def get_json_schema_guide() -> str:
    """获取 JSON Schema 使用说明"""
    return f"""# 漫画页面 JSON Schema

## 重要说明
**一个 JSON = 一页漫画（可包含多个分镜格）**

- **日式彩色漫画**：每页包含 4-8 个分镜格（`panels` 数组有 4-8 个元素）
- **中式/韩式漫画**：每页包含 1-3 个分镜格（`panels` 数组有 1-3 个元素）

## Schema 定义
{json.dumps(COMIC_PAGE_SCHEMA, indent=2, ensure_ascii=False)}

## 日式彩色漫画示例（一页多格，紧凑布局）
{json.dumps(COMIC_PANEL_EXAMPLES, indent=2, ensure_ascii=False)}



## 字段说明

### 必填字段
- `page_number`: 页码（整数，从1开始）
- `panels`: 分镜格数组（包含多个元素，数量由风格决定）
- `panel_number`: 格子编号（从1开始）
- `description`: 画面描述（字符串，必须详细）

### 可选字段
- `characters`: 出场角色数组
  - `name`: 角色名称（必填）
  - `action`: 动作描述
  - `expression`: 表情描述
  - `position_hint`: 位置提示

- `dialogues`: 对话数组
  - `speaker`: 说话人（必填）
  - `text`: 对话内容（必填）
  - `emotion`: 情绪
  - `position`: 气泡位置 {{x, y, width, height}}

- `background`: 背景描述
- `camera_angle`: 镜头角度
- `sound_effects`: 音效数组
- `layout`: 布局信息

- `page_notes`: 页面备注
- `layout_type`: 页面布局类型

## 不同风格的分镜策略

### 🇯🇵 日式彩色漫画（日漫风格/Manga）
- 每页 4-8 个格子
- 快速切换镜头，强调节奏
- 格子大小不一，有的跨栏突出重点
- 对话和动作分别用独立格子

### 🇨🇳 中式漫画（国风/中式风格）
- 每页 1-3 个格子
- 每个格子内容丰富，强调细节
- 格子较大，画面完整
- 可以在一个格子中包含多个动作
- 中国传统绘画元素和风格

### 🇰🇷 韩式漫画（韩式风格/Manhwa）
- 每页 1-3 个格子
- 每个格子内容丰富，强调细节
- 格子较大，画面完整
- 可以在一个格子中包含多个动作

### 🎨 其他风格（5个分镜彩色）
- 固定每页 5 个格子
- 特写的时候使用3个格子
- 彩色漫画风格
- 适合标准化分镜需求

## 描述字段（description）的写作要点

好的描述示例：
❌ "小明看到小猫" - 太简单，缺乏细节
✅ "中景镜头。小明（10岁男孩，黑色短发，穿着蓝色T恤）蹲在城市街道上，身体前倾，微笑着伸出右手。前方有一只橘色小猫，毛茸茸的，正抬头看着他。背景是街道的树木和建筑物，阳光透过树叶洒下斑驳光影。日漫风格，色彩明亮温馨。"

描述应包含：
- 镜头类型（全景/中景/特写等）
- 人物外貌和动作细节
- 位置关系
- 背景环境
- 光线和氛围
- 风格说明
"""
