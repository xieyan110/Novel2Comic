# 使用示例

本文档展示如何使用漫画服务 MCP 接口。

## 示例 1: 创建简单漫画

### 场景：将一段短文转换为漫画

**输入文本：**
```
小明走在街道上，看到了一只小猫。
"你好啊，小家伙！"小明笑着说。
小猫"喵"了一声，跑开了。
```

**步骤：**

#### 1. 生成人物参考图

```
工具调用：generate_character_reference

参数：
{
  "character_name": "小明",
  "description": "10岁男孩，短发，穿着蓝色T恤和牛仔裤，背着书包",
  "visual_features": {
    "hair_color": "黑色",
    "clothing": "蓝色T恤和牛仔裤",
    "age_range": "10岁左右"
  },
  "style": "日漫风格"
}

返回：
{
  "character_id": "char_小明",
  "name": "小明",
  "image_saved": "./config/references/characters/char_小明.jpg",
  "visual_features": {...}
}
```

#### 2. 生成场景参考图

```
工具调用：generate_scene_reference

参数：
{
  "scene_name": "街道",
  "description": "现代城市街道，有树木和建筑物，阳光明媚",
  "tags": ["城市", "街道", "白天"],
  "style": "日漫风格"
}

返回：
{
  "scene_id": "scene_街道",
  "name": "街道",
  "image_saved": "./config/references/scenes/scene_街道.jpg",
  "tags": ["城市", "街道", "白天"]
}
```

#### 3. 生成分镜 JSON

```
工具调用：generate_page_json

参数：
{
  "page_number": 1,
  "text": "小明走在街道上，看到了一只小猫。\n"你好啊，小家伙！\\"小明笑着说。\n小猫\\"喵\\"了一声，跑开了。"
}

返回：
{
  "page_number": 1,
  "panels": [
    {
      "panel_number": 1,
      "characters": [{
        "character_id": "char_小明",
        "character_name": "小明",
        "position": {"x": 0.3, "y": 0.5, "scale": 1.0},
        "action": "行走"
      }],
      "dialogues": [],
      "background": "街道",
      "background_ref": "scene_街道",
      "camera_angle": "全景",
      "description": "小明走在街道上"
    },
    {
      "panel_number": 2,
      "characters": [{
        "character_id": "char_小明",
        "character_name": "小明",
        "position": {"x": 0.5, "y": 0.5, "scale": 1.2},
        "action": "蹲下",
        "expression": "微笑"
      }],
      "dialogues": [{
        "speaker": "小明",
        "text": "你好啊，小家伙！",
        "position": {"x": 0.7, "y": 0.3, "width": 0.2, "height": 0.1},
        "emotion": "喜悦"
      }],
      "background": "街道",
      "camera_angle": "中景",
      "description": "小明看到小猫，微笑着打招呼"
    },
    {
      "panel_number": 3,
      "characters": [{
        "character_id": "char_小明",
        "character_name": "小明",
        "position": {"x": 0.3, "y": 0.5, "scale": 0.8},
        "action": "站立",
        "expression": "惊讶"
      }],
      "dialogues": [],
      "background": "街道",
      "camera_angle": "中景",
      "sound_effects": ["喵"],
      "description": "小猫跑开，小明惊讶地看着"
    }
  ],
  "page_notes": "第一页，三个分镜"
}
```

#### 4. 验证 JSON

```
工具调用：validate_json

参数：
{
  "page_json": "{...上面生成的 JSON...}",
  "original_text": "小明走在街道上..."
}

返回：
{
  "valid": true,
  "dialogues_count": 1,
  "panels_count": 3,
  "warnings": []
}
```

#### 5. 生成漫画图片

```
工具调用：generate_panel_image

参数：
{
  "page_number": 1,
  "panel_description": "第一格：日漫风格，全景镜头。小明（黑色短发，蓝色T恤）走在现代城市街道上，阳光明媚，街道两旁有树木和建筑物。",
  "character_refs": ["char_小明"],
  "scene_refs": ["scene_街道"],
  "image_size": "4K",
  "aspect_ratio": "3:4"
}

返回：
{
  "page_number": 1,
  "image_saved": "./output/pages/page_001.jpg",
  "character_refs_used": ["char_小明"],
  "scene_refs_used": ["scene_街道"]
}
```

## 示例 2: 批量生成多页

```
工具调用：batch_generate_pages

参数：
{
  "pages": [1, 2, 3, 4, 5],
  "concurrent_limit": 2
}

返回：
"已生成 5 页
- 第 1 页已保存: ./output/pages/page_001.jpg
- 第 2 页已保存: ./output/pages/page_002.jpg
- 第 3 页已保存: ./output/pages/page_003.jpg
- 第 4 页已保存: ./output/pages/page_004.jpg
- 第 5 页已保存: ./output/pages/page_005.jpg"
```

## 示例 3: 查看已创建的资源

```
工具调用：list_characters

返回：
[
  {
    "character_id": "char_小明",
    "name": "小明",
    "description": "10岁男孩，短发，穿着蓝色T恤...",
    "usage_count": 5
  },
  {
    "character_id": "char_小红",
    "name": "小红",
    "description": "10岁女孩，长发...",
    "usage_count": 3
  }
]
```

```
工具调用：list_scenes

返回：
[
  {
    "scene_id": "scene_街道",
    "name": "街道",
    "description": "现代城市街道...",
    "tags": ["城市", "街道", "白天"],
    "usage_count": 5
  }
]
```

## 示例 4: 更新人物参考图

如果你觉得某个角色的参考图不够理想，可以更新它：

```
工具调用：update_character_reference

参数：
{
  "character_id": "char_小明",
  "new_description": "10岁男孩，短发，穿着红色T恤和黑色短裤，运动鞋"
}

返回：
{
  "character_id": "char_小明",
  "name": "小明",
  "image_updated": "./config/references/characters/char_小明.jpg"
}
```

## 示例 5: 完整工作流（使用大模型）

当使用支持 MCP 的大模型（如 Claude）时，你可以直接用自然语言描述：

```
你：
我想制作一个简单的漫画，故事是这样的：
小明走在街道上，看到了一只小猫。
"你好啊，小家伙！"小明笑着说。
小猫"喵"的一声跑开了。

请帮我：

1. 先为小明生成一个人物参考图
2. 生成一个街道场景的参考图
3. 创建第1页的分镜JSON
4. 生成第1页的漫画图片
```

大模型会自动调用相应的 MCP 工具，完成整个流程。

## 提示词优化建议

### 生成人物参考图时

好的提示词：
```
"15岁少女，齐肩长发，穿着校服（白色衬衫、蓝色短裙），背着书包，
表情温柔，眼神清澈，日漫风格，全身正面照"
```

包含要素：
- 年龄和性别
- 发型
- 服装细节
- 配饰（书包）
- 表情和气质
- 风格
- 构图要求（全身正面照）

### 生成场景参考图时

好的提示词：
```
"日式校园中庭，樱花树盛开，花瓣飘落，有石桌和长椅，
阳光透过树叶洒下斑驳光影，宁静的氛围，日漫风格"
```

包含要素：
- 场景类型（校园中庭）
- 主要元素（樱花树、石桌、长椅）
- 氛围细节（花瓣飘落、斑驳光影）
- 光线描述
- 情绪氛围
- 风格

### 生成分镜时

好的提示词：
```
"第一格：中景镜头。小明（黑色短发，蓝色T恤）蹲在街道上，
微笑着伸出手，前方有一只小猫（橘色，毛茸茸）。
背景是现代城市街道，阳光明媚。
日漫风格，色彩明亮温馨。"
```

包含要素：
- 镜头类型（中景）
- 人物动作和位置
- 人物外貌参考
- 场景背景
- 光线
- 风格和色调
