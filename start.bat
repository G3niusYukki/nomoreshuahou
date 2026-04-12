@echo off
chcp 65001 >nul
echo ========================================
echo   Snap Buy - Coding Plan 自动抢购工具
echo ========================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 未找到虚拟环境，请先运行以下命令：
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo   playwright install chromium
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查配置文件
if not exist "config.yaml" (
    echo [提示] 未找到 config.yaml，正在生成示例配置...
    python main.py generate-config
    copy config.example.yaml config.yaml
    echo.
    echo 请编辑 config.yaml 配置文件，然后重新运行此脚本。
    pause
    exit /b 1
)

REM 显示菜单
:menu
echo.
echo 请选择操作：
echo   1. 运行抢购 (run)
echo   2. 登录阿里云 (login aliyun)
echo   3. 登录GLM (login glm)
echo   4. 验证配置 (test-config)
echo   5. 查看平台状态 (list-platforms)
echo   6. 退出
echo.
set /p choice="请输入选项 (1-6): "

if "%choice%"=="1" goto run
if "%choice%"=="2" goto login_aliyun
if "%choice%"=="3" goto login_glm
if "%choice%"=="4" goto test_config
if "%choice%"=="5" goto list_platforms
if "%choice%"=="6" goto exit
echo 无效选项，请重新输入。
goto menu

:run
echo.
echo 正在启动抢购程序...
echo 按 Ctrl+C 可以停止程序
echo.
python main.py run
pause
goto menu

:login_aliyun
echo.
echo 正在打开阿里云登录页面...
echo 请在浏览器中完成登录，然后在此按 Enter
python main.py login aliyun
pause
goto menu

:login_glm
echo.
echo 正在打开GLM登录页面...
echo 请在浏览器中完成登录，然后在此按 Enter
python main.py login glm
pause
goto menu

:test_config
echo.
python main.py test-config
pause
goto menu

:list_platforms
echo.
python main.py list-platforms
pause
goto menu

:exit
echo.
echo 再见！
pause
exit /b 0
