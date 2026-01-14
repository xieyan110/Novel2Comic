"""
漫画服务启动脚本
"""

import asyncio
import os
import sys
from pathlib import Path

# 设置 UTF-8 编码输出（通过环境变量，更安全）
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


async def main():
    """启动 MCP 服务器"""
    from src.mcp_server import main as server_main

    # 检查 API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("Warning: GEMINI_API_KEY not set")
        print("Please configure your Gemini API Key in .env file")
        print("\nGet API Key: https://aistudio.google.com/app/apikey")
        return

    print("Comic Service MCP Server starting...")
    print(f"Project path: {Path(__file__).parent}")
    print(f"API Key: {api_key[:10]}...")
    print("\nServer started, waiting for connection...\n")

    await server_main()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nServer stopped")
