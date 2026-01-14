# 快速开始指南

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

## 2. 配置 API Key

### 方式一：使用 .env 文件（推荐）

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 Gemini API Key
# GEMINI_API_KEY=your_actual_api_key_here
```

### 方式二：直接设置环境变量

```bash
export GEMINI_API_KEY=your_api_key_here  # Linux/Mac
set GEMINI_API_KEY=your_api_key_here     # Windows
```

### 获取 API Key

访问 [Google AI Studio](https://aistudio.google.com/app/apikey) 获取免费的 Gemini API Key。

## 3. 启动 MCP 服务器

```bash
python start_server.py
```

成功启动后，你会看到：

```
🎨 漫画服务 MCP 服务器启动中...
📂 项目路径: /path/to/comic_service
🔑 API Key: AIzaSy...
✨ 服务器已启动，等待连接...
```

## 4. 配置 MCP 客户端

### 使用 Claude Desktop

编辑 Claude Desktop 配置文件（通常在 `~/Library/Application Support/Claude/claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "comic-service": {
      "command": "python",
      "args": ["/path/to/comic_service/start_server.py"],
      "env": {
        "GEMINI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### 使用其他 MCP 客户端

参考项目根目录的 `config/mcp_config.json` 文件。

## 5. 使用示例

### 完整工作流程

```
===== 第一步：生成人物参考图 =====
"请为以下角色生成参考图：
- 刘备：面如冠玉，耳垂过大，身穿黄色长袍
- 关羽：面如重枣，长髯，穿绿袍
- 张飞：豹头环眼，燕颔虎须，穿黑甲"

MCP 工具调用：
1. generate_character_reference("刘备", "面如冠玉...")
2. generate_character_reference("关羽", "面如重枣...")
3. generate_character_reference("张飞", "豹头环眼...")

===== 第二步：生成场景参考图 =====
"生成以下场景的参考图：
- 桃园：春日，桃花盛开
- 战场：古战场，硝烟弥漫"

MCP 工具调用：
4. generate_scene_reference("桃园", "春日...")
5. generate_scene_reference("战场", "古战场...")

===== 第三步：生成分镜 JSON =====
"这是第一章的文本：[文本内容]，请生成第1页的分镜JSON"

MCP 工具调用：
6. generate_page_json(page_number=1, text="...")

===== 第四步：生成漫画图片 =====
"现在生成第1页的漫画图片"

MCP 工具调用：
7. generate_panel_image(
     page_number=1,
     panel_description="刘备、关羽、张飞三人站在桃园中...",
     character_refs=["char_刘备", "char_关羽", "char_张飞"],
     scene_refs=["scene_桃园"]
   )

===== 第五步：批量生成 =====
"批量生成第2-10页"

MCP 工具调用：
8. batch_generate_pages(pages=[2,3,4,5,6,7,8,9,10])

===== 第六步：导出项目 =====
9. export_project(format="json")
```

## 项目结构

```
comic_service/
├── src/                     # 源代码
│   ├── mcp_server.py        # MCP 服务器主入口
│   ├── models/              # 数据模型
│   ├── image_gen/           # 图片生成模块
│   ├── parsers/             # 文本解析器
│   └── ...
├── config/                  # 配置文件
│   ├── gemini_config.json   # Gemini API 配置
│   └── references/          # 参考图存储
│       ├── characters/      # 人物参考图
│       └── scenes/          # 场景参考图
├── output/                  # 输出目录
│   └── pages/               # 生成的漫画图片
├── start_server.py          # 启动脚本
└── requirements.txt         # Python 依赖
```

## 可用工具列表

### 核心工具
- `generate_overview` - 生成漫画总览
- `generate_page_json` - 生成单页分镜 JSON
- `validate_json` - 验证 JSON 完整性
- `preview_page` - 预览单页内容

### 图片生成工具
- `generate_character_reference` - 生成人物参考图
- `generate_scene_reference` - 生成场景参考图
- `generate_panel_image` - 生成单页分镜图片
- `regenerate_single_panel` - 重新生成特定分镜
- `batch_generate_pages` - 批量生成多页图片

### 管理工具
- `list_characters` - 列出所有已生成的人物参考图
- `list_scenes` - 列出所有已生成的场景参考图
- `update_character_reference` - 更新人物参考图
- `export_project` - 导出完整项目

## 常见问题

### 1. API 调用失败

检查：
- API Key 是否正确
- 网络连接是否正常
- 是否达到 API 限流

### 2. 图片生成速度慢

- 调整 `image_size` 参数（使用 2K 或 1K）
- 减少 `concurrent_limit` 参数
- 检查网络延迟

### 3. 人物不一致

- 确保每次生成都使用了正确的 `character_refs`
- 检查参考图是否正确生成
- 可以使用 `update_character_reference` 更新参考图

## 下一步

查看 [README.md](README.md) 了解更多详细信息。

查看 `examples/` 目录获取更多使用示例。
