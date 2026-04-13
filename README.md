# Snap Buy - Coding Plan 自动抢购工具

一个基于 Python + Playwright 的自动化抢购工具，支持阿里云百炼 Coding Plan 和 GLM Coding Plan。

## 功能特点

- 🚀 **双平台支持**：同时支持阿里云百炼和GLM两个平台
- ⏰ **精准定时**：秒级精度的定时触发，确保在补货瞬间抢购
- 🔄 **智能重试**：指数退避重试机制，自动处理网络波动
- 🛡️ **反检测**：内置反爬虫措施，模拟真实用户行为
- 📱 **即时通知**：抢购成功/失败即时通知（桌面+声音）
- 🔐 **会话保持**：登录状态持久化，避免重复扫码
- ⚙️ **灵活配置**：YAML配置文件，支持自定义套餐优先级

## 系统要求

- Python 3.14+
- Windows/macOS/Linux
- 网络连接

## 安装步骤

### 1. 克隆或下载项目

```bash
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
```

### 4. 安装 Playwright 浏览器

```bash
playwright install chromium
```

## 配置

### 1. 生成配置文件

```bash
python main.py generate-config
```

### 2. 复制并编辑配置

```bash
cp config.example.yaml config.yaml
```

### 3. 编辑 config.yaml

```yaml
scheduler:
  timezone: Asia/Shanghai
  pre_warm_seconds: 30  # 提前30秒预热浏览器

platforms:
  aliyun:
    enabled: true
    purchase_time: '09:30:00'  # 阿里云每天9:30补货
    url: https://common-buy.aliyun.com/coding-plan
    max_retries: 5
    retry_delay_seconds: 1.0
    
  glm:
    enabled: true
    purchase_time: '10:00:00'  # GLM每天10:00补货
    url: https://www.bigmodel.cn/glm-coding
    max_retries: 5
    retry_delay_seconds: 1.0
    priority:  # 套餐优先级，按顺序尝试
      - Pro
      - Lite
      - Max

browser:
  headless: false  # 建议false，便于观察和扫码登录
  slow_mo: 50      # 操作间隔(毫秒)，模拟人类速度
  viewport_width: 1920
  viewport_height: 1080

notification:
  sound_enabled: true
  sound_file: null  # 可指定WAV文件路径
  desktop_enabled: true
  log_file: logs/snap_buy.log
```

## 使用方法

### 1. 登录账号

首次使用需要手动登录，保存会话状态：

```bash
# 登录阿里云
python main.py login aliyun

# 登录GLM
python main.py login glm
```

程序会打开浏览器，你需要手动完成登录（扫码或输入账号密码），然后在终端按 Enter 确认。

### 2. 验证配置

```bash
python main.py test-config
```

### 3. 查看平台状态

```bash
python main.py list-platforms
```

### 4. 运行抢购

```bash
python main.py run
```

程序会：
1. 根据配置的时间自动调度抢购任务
2. 提前30秒预热浏览器并打开购买页面
3. 在补货时间点精准触发购买
4. 自动重试直到成功或达到最大次数
5. 抢购成功后发送桌面通知和声音提示

## 工作原理

```
┌─────────────────────────────────────────────────────────┐
│                    Snap Buy 主程序                        │
├─────────────────────────────────────────────────────────┤
│              APScheduler 定时调度器                        │
│         (每天 9:30 阿里云, 10:00 GLM)                     │
├─────────────────┬───────────────────────────────────────┤
│                 │                                        │
│  ┌──────────────▼──────────────┐                        │
│  │      浏览器预热模块          │                        │
│  │  (提前30秒打开购买页面)      │                        │
│  └──────────────┬──────────────┘                        │
│                 │                                        │
│  ┌──────────────▼──────────────┐                        │
│  │      精准定时触发            │                        │
│  │  (毫秒级时间对齐)           │                        │
│  └──────────────┬──────────────┘                        │
│                 │                                        │
│  ┌──────────────▼──────────────┐                        │
│  │      自动购买流程            │                        │
│  │  - 检测可用性               │                        │
│  │  - 点击购买按钮             │                        │
│  │  - 确认订单                 │                        │
│  └──────────────┬──────────────┘                        │
│                 │                                        │
│  ┌──────────────▼──────────────┐                        │
│  │      通知模块                │                        │
│  │  - 桌面通知                 │                        │
│  │  - 声音提示                 │                        │
│  │  - 日志记录                 │                        │
│  └─────────────────────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

## 常见问题

### Q: 为什么选择 Playwright 而不是 Selenium？

A: Playwright 相比 Selenium 有以下优势：
- 更快的执行速度
- 自动等待元素，无需手动 sleep
- 更好的反检测能力
- 更现代的 API 设计

### Q: 登录状态能保持多久？

A: 登录状态会保存在 `auth/` 目录下，通常可以保持数天到数周。如果过期，程序会提示你重新登录。

### Q: 可以只抢一个平台吗？

A: 可以，在 config.yaml 中将不需要的平台设置为 `enabled: false`。

### Q: GLM的套餐优先级是什么意思？

A: 如果你设置了 `priority: [Pro, Lite, Max]`，程序会按顺序尝试：
1. 先尝试购买 Pro 套餐
2. 如果 Pro 售罄，尝试 Lite
3. 如果 Lite 也售罄，尝试 Max

### Q: 抢购失败怎么办？

A: 程序会自动重试（默认5次），并记录日志到 `logs/snap_buy.log`。你也可以查看 `logs/screenshots/` 目录下的截图来诊断问题。

### Q: 会违反平台规定吗？

A: 本工具仅用于自动化浏览器操作，模拟手动抢购过程。请注意：
- 仅用于个人订阅抢购
- 不要用于批量抢购或商业用途
- 遵守平台的服务条款

## 目录结构

```
snap-buy/
├── main.py              # CLI入口
├── config.example.yaml  # 示例配置
├── requirements.txt     # 依赖列表
├── core/               # 核心模块
│   ├── browser.py      # 浏览器管理
│   ├── config.py       # 配置加载
│   ├── notifier.py     # 通知系统
│   ├── retry.py        # 重试机制
│   └── scheduler.py    # 定时调度
├── platforms/          # 平台实现
│   ├── base.py         # 基类
│   ├── aliyun/         # 阿里云
│   │   ├── buyer.py    # 购买流程
│   │   └── login.py    # 登录处理
│   └── glm/            # GLM
│       ├── buyer.py    # 购买流程
│       └── login.py    # 登录处理
├── auth/               # 会话状态（gitignore）
├── logs/               # 日志文件（gitignore）
└── tests/              # 测试文件
```

## 开发说明

### 运行测试

```bash
pytest tests/
```

### 代码风格

项目使用 Python 类型提示和现代化的异步编程模式。

## 许可证

MIT License

## 免责声明

本工具仅供学习和个人使用。使用本工具造成的任何后果由使用者自行承担。请遵守相关平台的服务条款。
