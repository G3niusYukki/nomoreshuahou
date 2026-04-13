# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Snap Buy is an automated purchase tool for coding plan subscriptions (Aliyun百炼 and GLM). It uses Playwright for browser automation, APScheduler for scheduling, and follows a plugin-like platform architecture.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run via CLI (all commands use Click)
python main.py run                          # Start the scheduler
python main.py login aliyun                  # Login to Aliyun
python main.py login glm                     # Login to GLM
python main.py test-config                  # Validate config.yaml
python main.py list-platforms                # Show platform status
python main.py generate-config               # Generate config.example.yaml

# Run tests (tests/ is empty - no test suite exists yet)
pytest tests/
```

On Windows, use `install.bat` / `start.bat` scripts instead.

## Architecture

```
main.py (Click CLI) → core.* (infrastructure) → platforms/* (implementations)
```

### Core modules (`core/`)

| Module | Responsibility |
|--------|----------------|
| `config.py` | Pydantic models + YAML loading. `AppConfig` is the root. All config values validated here. |
| `browser.py` | `BrowserManager` wraps Playwright. Handles context creation, stealth injection (webdriver override, plugin spoofing), and session persistence (`auth/*.json`). |
| `scheduler.py` | `PurchaseScheduler` wraps APScheduler's `AsyncIOScheduler`. The key behavior: **pre-warms browser 30s before purchase time, then busy-waits (20ms polling) to align to sub-second precision**. |
| `retry.py` | `retry_async()` with exponential backoff. Error classification: "sold out"/"captcha" → terminal (no retry); everything else → retryable. |
| `notifier.py` | Desktop notification (plyer) + system sound (winsound on Windows, aplay on Linux/macOS). |

### Platform layer (`platforms/`)

- `base.py` — `BaseBuyer` ABC: defines `check_login()`, `is_available()`, `execute_purchase()`. Both `pre_warm()` (opens page, returns BrowserContext) and `run()` (full purchase flow) are here.
- `aliyun/buyer.py` — `AliyunBuyer`: single-plan buyer. Falls back through `purchase_button` selectors, waits for `success_indicator`.
- `glm/buyer.py` — `GLMBuyer`: priority-ordered multi-tier buyer (`Pro > Lite > Max`). Has its own tier selectors and `SOLD_OUT_SELECTORS`.

Selectors in both buyers use Playwright's `query_selector` (not `locator`) — these return raw handles and must be explicitly awaited. All selectors are CSS/text-based strings that may need updating if the target pages change.

### Scheduler flow

```
schedule_platform() → CronTrigger at HH:MM:SS
  → wrapped():
      1. pre_warm=True  → buyer.pre_warm()  (opens page, returns context)
      2. align_to_target()  (busy-wait to exact second)
      3. pre_warm=False → buyer.run(context=context)  (executes purchase)
```

## Key Patterns

- **Auth persistence**: `auth/{platform}_state.json` stores Playwright `storage_state`. Loaded automatically on `run()`; created manually via `login` command.
- **Error classification**: Errors containing "sold out", "captcha", "forbidden" → `ErrorCategory.TERMINAL` (stops retrying). Everything else → exponential backoff retry.
- **No tests exist yet**: The `tests/` directory only has `__init__.py`.
- **Stealth**: `BrowserManager._apply_stealth()` injects a JS init script that overrides `navigator.webdriver`, `navigator.plugins`, `navigator.languages`, and `window.chrome`.
