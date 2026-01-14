"""
测试 Gemini API 客户端
用于验证 API 连接和基本功能
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from src.image_gen.gemini_client import GeminiImageGenerator

# 加载环境变量
load_dotenv()


async def test_gemini_client():
    """测试 Gemini 客户端"""

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("⚠️  请先设置 GEMINI_API_KEY 环境变量")
        return

    print("🧪 测试 Gemini API 客户端\n")

    # 初始化客户端
    client = GeminiImageGenerator(
        api_key=api_key,
        model="gemini-3-pro-image-preview"
    )

    # 测试 1: 生成人物参考图
    print("📝 测试 1: 生成人物参考图")
    print("-" * 50)

    try:
        character_image = await client.generate_character_reference(
            character_name="测试角色",
            description="年轻女子，长发，穿着白色连衣裙，站在花园中",
            style="日漫风格"
        )

        print("✅ 人物参考图生成成功！")
        print(f"   图片数据长度: {len(character_image)} 字符")

        # 保存图片
        output_dir = Path(__file__).parent.parent / "output" / "test"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / "test_character.jpg"
        client.save_base64_image(character_image, output_path)
        print(f"   图片已保存: {output_path}\n")

    except Exception as e:
        print(f"❌ 失败: {e}\n")

    # 测试 2: 生成场景参考图
    print("📝 测试 2: 生成场景参考图")
    print("-" * 50)

    try:
        scene_image = await client.generate_scene_reference(
            scene_name="测试场景",
            description="樱花盛开的日式庭院，有石灯笼和小桥",
            style="日漫风格"
        )

        print("✅ 场景参考图生成成功！")
        print(f"   图片数据长度: {len(scene_image)} 字符")

        # 保存图片
        output_path = output_dir / "test_scene.jpg"
        client.save_base64_image(scene_image, output_path)
        print(f"   图片已保存: {output_path}\n")

    except Exception as e:
        print(f"❌ 失败: {e}\n")

    # 测试 3: 携带参考图生成
    print("📝 测试 3: 携带参考图生成分镜")
    print("-" * 50)

    try:
        panel_image = await client.generate_with_references(
            prompt="日漫风格的漫画分镜：测试角色站在樱花树下，微笑着看向观众，温馨的氛围",
            image_refs=[character_image],  # 使用之前生成的角色图作为参考
            image_size="2K",
            aspect_ratio="3:4"
        )

        print("✅ 分镜图生成成功！")
        print(f"   图片数据长度: {len(panel_image)} 字符")

        # 保存图片
        output_path = output_dir / "test_panel.jpg"
        client.save_base64_image(panel_image, output_path)
        print(f"   图片已保存: {output_path}\n")

    except Exception as e:
        print(f"❌ 失败: {e}\n")

    print("=" * 50)
    print("✨ 测试完成！")
    print(f"📁 所有测试图片保存在: {output_dir}")


if __name__ == "__main__":
    try:
        asyncio.run(test_gemini_client())
    except KeyboardInterrupt:
        print("\n\n👋 测试已中断")
