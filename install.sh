#!/bin/bash

echo "========================================"
echo "  Snap Buy 安装脚本"
echo "========================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3，请先安装 Python 3.9+"
    exit 1
fi

echo "[1/5] 检测到 Python"
python3 --version

# 创建虚拟环境
echo ""
echo "[2/5] 创建虚拟环境..."
if [ -d "venv" ]; then
    echo "虚拟环境已存在，跳过"
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[错误] 创建虚拟环境失败"
        exit 1
    fi
    echo "虚拟环境创建成功"
fi

# 激活虚拟环境
echo ""
echo "[3/5] 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo ""
echo "[4/5] 安装依赖包..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[错误] 安装依赖失败"
    exit 1
fi

# 安装Playwright浏览器
echo ""
echo "[5/5] 安装 Playwright 浏览器..."
playwright install chromium
if [ $? -ne 0 ]; then
    echo "[警告] 安装浏览器失败，请手动运行: playwright install chromium"
fi

# 生成配置文件
echo ""
echo "生成配置文件..."
if [ ! -f "config.yaml" ]; then
    python main.py generate-config
    cp config.example.yaml config.yaml
    echo "已生成 config.yaml，请编辑此文件配置你的抢购参数"
fi

echo ""
echo "========================================"
echo "  安装完成！"
echo "========================================"
echo ""
echo "下一步："
echo "  1. 编辑 config.yaml 配置文件"
echo "  2. 运行 ./start.sh 启动程序"
echo "  3. 先登录账号（选项2或3）"
echo "  4. 然后运行抢购（选项1）"
echo ""
