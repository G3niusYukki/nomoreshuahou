#!/bin/bash

echo "========================================"
echo "  Snap Buy - Coding Plan 自动抢购工具"
echo "========================================"
echo ""

# 检查虚拟环境
if [ ! -f "venv/bin/activate" ]; then
    echo "[错误] 未找到虚拟环境，请先运行以下命令："
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo "  playwright install chromium"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查配置文件
if [ ! -f "config.yaml" ]; then
    echo "[提示] 未找到 config.yaml，正在生成示例配置..."
    python main.py generate-config
    cp config.example.yaml config.yaml
    echo ""
    echo "请编辑 config.yaml 配置文件，然后重新运行此脚本。"
    exit 1
fi

# 显示菜单
while true; do
    echo ""
    echo "请选择操作："
    echo "  1. 运行抢购 (run)"
    echo "  2. 登录阿里云 (login aliyun)"
    echo "  3. 登录GLM (login glm)"
    echo "  4. 验证配置 (test-config)"
    echo "  5. 查看平台状态 (list-platforms)"
    echo "  6. 退出"
    echo ""
    read -p "请输入选项 (1-6): " choice

    case $choice in
        1)
            echo ""
            echo "正在启动抢购程序..."
            echo "按 Ctrl+C 可以停止程序"
            echo ""
            python main.py run
            ;;
        2)
            echo ""
            echo "正在打开阿里云登录页面..."
            echo "请在浏览器中完成登录，然后在此按 Enter"
            python main.py login aliyun
            ;;
        3)
            echo ""
            echo "正在打开GLM登录页面..."
            echo "请在浏览器中完成登录，然后在此按 Enter"
            python main.py login glm
            ;;
        4)
            echo ""
            python main.py test-config
            ;;
        5)
            echo ""
            python main.py list-platforms
            ;;
        6)
            echo ""
            echo "再见！"
            exit 0
            ;;
        *)
            echo "无效选项，请重新输入。"
            ;;
    esac
done
