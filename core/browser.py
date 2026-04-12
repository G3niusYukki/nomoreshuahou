from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from core.config import BrowserConfig

logger = logging.getLogger(__name__)

AUTH_DIR = Path(__file__).resolve().parent.parent / "auth"


class BrowserManager:
    def __init__(self, config: BrowserConfig):
        self.config = config
        self._playwright = None
        self._browser: Optional[Browser] = None

    async def launch(self) -> Browser:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.config.headless,
            slow_mo=self.config.slow_mo,
        )
        return self._browser

    async def create_context(
        self,
        storage_state_path: Optional[Path] = None,
    ) -> BrowserContext:
        if self._browser is None:
            await self.launch()

        state = None
        if storage_state_path and storage_state_path.exists():
            logger.info(f"Loading session state from {storage_state_path}")
            state = str(storage_state_path)

        context = await self._browser.new_context(
            storage_state=state,
            viewport=self.config.viewport,
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )

        # Apply stealth patches
        await self._apply_stealth(context)
        return context

    async def _apply_stealth(self, context: BrowserContext) -> None:
        """Apply stealth patches to avoid detection."""
        stealth_js = """
        // Override webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Override plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Override languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en-US', 'en']
        });
        
        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Chrome runtime
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
        """
        await context.add_init_script(stealth_js)

    @staticmethod
    async def save_state(context: BrowserContext, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        await context.storage_state(path=str(path))
        logger.info(f"Session state saved to {path}")

    @staticmethod
    async def new_page(context: BrowserContext) -> Page:
        page = await context.new_page()
        return page

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
