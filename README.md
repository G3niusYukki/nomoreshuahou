# Snap Buy - Coding Plan 自动抢购工具

一个基于 Python + Playwright 的自动化抢购工具，支持阿里云百炼 Coding Plan 和 GLM Coding Plan。

## 功能特点

- **双平台支持**：同时支持阿里云百炼和 GLM 两个平台
- **精准定时**：秒级精度的定时触发，提前预热浏览器，确保在补货瞬间抢购
- **智能重试**：指数退避重试机制，自动处理网络波动
- **反检测**：playwright-stealth 反爬虫，隐藏自动化特征
- **即时通知**：抢购成功/失败即时通知（桌面 + 声音）
- **会话保持**：登录状态持久化，避免重复扫码
- **手动支付**：抢到后暂停等待扫码/密码支付，不自动扣费
- **代理支持**：支持配置 HTTP 代理，适应不同网络环境
- **立即模式**：`--now` 跳过调度，立即执行一次抢购（调试用）

## 系统要求

- Python 3.11+
- Windows / macOS / Linux
- 网络连接

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/G3niusYukki/nomoreshuahou.git
cd snap-buy
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

## 配置

### 1. 生成配置文件

```bash
python main.py generate-config
cp config.example.yaml config.yaml
```

### 2. 编辑 config.yaml

```yaml
scheduler:
  timezone: Asia/Shanghai
  pre_warm_seconds: 30

platforms:
  aliyun:
    enabled: true
    purchase_time: '09:30:00'
    url: https://www.aliyun.com/benefit/scene/codingplan
    max_retries: 5
    retry_delay_seconds: 1.0
    payment_timeout: 120    # 支付等待超时（秒）

  glm:
    enabled: true
    purchase_time: '10:00:00'
    url: https://www.bigmodel.cn/glm-coding
    max_retries: 5
    retry_delay_seconds: 1.0
    payment_timeout: 120
    priority:               # 套餐优先级
      - Pro
      - Lite
      - Max

browser:
  headless: false           # 建议关闭，便于观察
  slow_mo: 50
  viewport_width: 1920
  viewport_height: 1080
  proxy: null               # 例: http://127.0.0.1:7897

notification:
  sound_enabled: true
  sound_file: null
  desktop_enabled: true
  log_file: logs/snap_buy.log
```

## 使用方法

### 1. 登录账号

首次使用需要手动登录，保存会话状态：

```bash
python main.py login aliyun
python main.py login glm
```

程序会打开浏览器，手动完成登录后在终端按 Enter 确认。会话保存在 `auth/` 目录。

### 2. 立即测试

```bash
# 跳过调度，立即执行一次购买流程
python main.py run --now
```

### 3. 定时运行

```bash
# 按配置的时间自动调度
python main.py run
```

### 其他命令

```bash
python main.py test-config      # 验证配置文件
python main.py list-platforms   # 查看平台状态
python main.py generate-config  # 生成示例配置
```

## 购买流程

### 阿里云百炼

1. 打开购买页面 `https://www.aliyun.com/benefit/scene/codingplan`
2. 点击「马上抢购」→ 跳转到订阅页面
3. 检测售罄状态，若有库存则点击「订阅」
4. 确认订单 → 等待手动支付 → 桌面通知提醒

### GLM

1. 打开 `https://www.bigmodel.cn/glm-coding`
2. 按优先级选择套餐（Pro → Lite → Max）
3. 检测每个套餐的库存状态
4. 有库存则点击购买按钮 → 等待支付

## 目录结构

```
snap-buy/
├── main.py                # CLI 入口（Click）
├── config.example.yaml    # 示例配置
├── requirements.txt       # 依赖列表
├── core/                  # 核心模块
│   ├── browser.py         # 浏览器管理 + stealth 注入
│   ├── config.py          # Pydantic 配置模型
│   ├── notifier.py        # 桌面通知 + 声音
│   ├── retry.py           # 指数退避重试
│   └── scheduler.py       # APScheduler 定时调度
├── platforms/             # 平台实现
│   ├── base.py            # BaseBuyer 基类
│   ├── base_login.py      # BaseLoginHandler 基类
│   ├── aliyun/
│   │   ├── buyer.py       # 阿里云购买流程
│   │   └── login.py       # 阿里云登录
│   └── glm/
│       ├── buyer.py       # GLM 购买流程
│       └── login.py       # GLM 登录
├── auth/                  # 会话状态（gitignore）
└── logs/                  # 日志和截图（gitignore）
```

## 常见问题

**Q: 登录状态能保持多久？**
会话保存在 `auth/*.json`，通常可保持数天到数周。过期后程序会提示重新登录。

**Q: 可以只抢一个平台吗？**
在 config.yaml 中将不需要的平台设为 `enabled: false`。

**Q: 如何调试？**
使用 `python main.py run --now` 立即执行一次，观察浏览器行为。日志在 `logs/snap_buy.log`，错误截图在 `logs/screenshots/`。

**Q: 需要代理吗？**
如果网络受限，在 config.yaml 中设置 `browser.proxy: http://127.0.0.1:端口`。

## 免责声明

本工具仅供学习和个人使用。使用本工具造成的任何后果由使用者自行承担。请遵守相关平台的服务条款。
