# Novel2Comic 🎨

把小说变成日漫风格漫画的MCP小工具。(我没有试过国风，因为太费页了，接口太贵了)
![alt text](image.png)

## 怎么安装

### 1. 配置 MCP 服务

**先搞定 API Key**

打开 [.mcp.json](.mcp.json)，把你的 API Key 填进去。

**用的模型**

- `gemini-3-pro-image-preview` 画图用的

**API 代理**

- 推荐用 [uniapi.io](https://uniapi.ai/register?aff=LEGx)

**装 Python 依赖**

先进入 comic_service 里面
```bash
pip install -r requirements.txt
```

创建**comic_service\.env**内容如下（key 直接通过.mcp.json 文件就行）：

```
# Gemini API 配置
GEMINI_API_KEY=sk-xxxxxxx
GEMINI_API_BASE_URL=https://api.uniapi.io
GEMINI_MODEL=gemini-3-pro-image-preview

# 存储路径
REFERENCE_IMAGES_PATH=./config/references
OUTPUT_IMAGES_PATH=./output/pages

# 日志级别
LOG_LEVEL=INFO

```


### 2. 配置 Claude Code

**API 服务选哪个都行**

- [智谱 AI](https://open.bigmodel.cn/special_area) （推荐）
- [豆包](https://www.volcengine.com/activity/codingplan)

价格差不多，看你喜好。

**装 VSCode 插件**

- [Claude Code 插件](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code)

## 怎么用

### 简单用法

直接跟 Claude Code 说：

```
把 @小说/小说.txt 转成日本漫画，我已经生成了两个人物参考图。
2k 分辨率，尽量用奇数格的布局
```

### 参数啥意思

| 参数 | 说啥 |
|------|------|
| `@小说/小说.txt` | 你的小说文件在哪 |
| `人物参考图` | 第一次不用管，AI 会自动生成；后面就会用已有的 |
| `2k` | 图片清晰度（可以是 1k、2k、4k） |
| `奇数格` | 漫画排版喜欢奇数格 |

### 高级玩法

**某页不好看？重新生成**

直接告诉 AI：

```
第 6 页不行，重新生成一下
```

AI 会找到对应的 JSON 配置重新画。

## 原理是啥

1. AI 读你的小说，搞清楚场景和角色
2. 第一次会生成人物参考图
3. 然后给每一页生成 JSON 配置
4. 用配置调用画图 API
5. 搞定，漫画出来

## 常见问题

**Q: 人物参考图不满意咋办？**
A: 让 AI 重新生成那个角色的参考图就行。

**Q: 支持其他漫画风格吗？**
A: 目前主要是日漫风格。

**Q: 画面比例能改吗？**
A: 可以啊，3:4、16:9、9:16 这些都支持。
