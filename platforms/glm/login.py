from __future__ import annotations

import logging
from pathlib import Path

from playwright.async_api import BrowserContext, Page

from core.browser import BrowserManager, AUTH_DIR
from core.config import BrowserConfig

logger = logging.getLogger(__name__)


class GLMLoginHandler:
    LOGIN_URL = "https://open.bigmodel.cn/login"
    USER_CENTER_URL = "https://open.bigmodel.cn/usercenter"

    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager
        self.auth_path = AUTH_DIR / "glm_state.json"

    async def login(self) -> BrowserContext:
        logger.info("Opening GLM login page for manual authentication...")
        logger.info("Log in via WeChat scan or account credentials.")

        context = await self.browser_manager.create_context()
        page = await BrowserManager.new_page(context)

        await page.goto(self.LOGIN_URL, wait_until="domcontentloaded")
        logger.info("Waiting for manual login... Press Enter in console when done.")

        input(">>> Press Enter after you have completed login in the browser...")

        # Verify login
        await page.goto(self.USER_CENTER_URL, wait_until="domcontentloaded")
        await page.wait_for_load_state("networkidle")

        if "login" in page.url.lower():
            logger.error("Login verification failed")
            raise RuntimeError("Login failed: still on login page after manual attempt")

        logger.info("Login verified! Saving session state...")
        await BrowserManager.save_state(context, self.auth_path)
        logger.info(f"Session state saved to {self.auth_path}")
        return context

    async def check_and_reauth(self, context: BrowserContext) -> bool:
        page = await BrowserManager.new_page(context)
        await page.goto(self.USER_CENTER_URL, wait_until="domcontentloaded")
        await page.wait_for_load_state("networkidle")

        if "login" in page.url.lower():
            logger.warning("GLM session expired, re-authentication needed")
            return False
        logger.info("GLM session is valid")
        return True
