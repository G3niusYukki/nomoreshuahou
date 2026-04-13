@echo off
chcp 65001 >nul
echo ========================================
echo   Snap Buy 安装脚本
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.14+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] 检测到 Python
python --version

REM 创建虚拟环境
echo.
echo [2/5] 创建虚拟环境...
if exist "venv" (
    echo 虚拟环境已存在，跳过
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功
)

REM 激活虚拟环境
echo.
echo [3/5] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo.
echo [4/5] 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 安装依赖失败
    pause
    exit /b 1
)

REM 安装Playwright浏览器
echo.
echo [5/5] 安装 Playwright 浏览器...
playwright install chromium
if errorlevel 1 (
    echo [警告] 安装浏览器失败，请手动运行: playwright install chromium
)

REM 生成配置文件
echo.
echo 生成配置文件...
if not exist "config.yaml" (
    python main.py generate-config
    copy config.example.yaml config.yaml
    echo 已生成 config.yaml，请编辑此文件配置你的抢购参数
)

echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 下一步：
echo   1. 编辑 config.yaml 配置文件
echo   2. 运行 start.bat 启动程序
echo   3. 先登录账号（选项2或3）
echo   4. 然后运行抢购（选项1）
echo.
pause
