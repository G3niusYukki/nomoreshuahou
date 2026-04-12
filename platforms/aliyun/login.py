from __future__ import annotations

import logging
from pathlib import Path

from playwright.async_api import BrowserContext, Page

from core.browser import BrowserManager, AUTH_DIR
from core.config import BrowserConfig

logger = logging.getLogger(__name__)


class AliyunLoginHandler:
    LOGIN_URL = "https://login.aliyun.com/"
    ACCOUNT_URL = "https://account.aliyun.com/"

    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager
        self.auth_path = AUTH_DIR / "aliyun_state.json"

    async def login(self) -> BrowserContext:
        logger.info("Opening Aliyun login page for manual authentication...")
        logger.info("Please log in using your browser (QR code or credentials).")

        context = await self.browser_manager.create_context()
        page = await BrowserManager.new_page(context)

        await page.goto(self.LOGIN_URL, wait_until="domcontentloaded")
        logger.info("Waiting for manual login... Press Enter in console when done.")

        # Wait for user to complete login manually
        input(">>> Press Enter after you have completed login in the browser...")

        # Verify login by navigating to account page
        await page.goto(self.ACCOUNT_URL, wait_until="domcontentloaded")
        if "login" in page.url.lower():
            logger.error("Login verification failed - still on login page")
            raise RuntimeError("Login failed: still on login page after manual attempt")

        logger.info("Login verified! Saving session state...")
        await BrowserManager.save_state(context, self.auth_path)
        logger.info(f"Session state saved to {self.auth_path}")
        return context

    async def check_and_reauth(self, context: BrowserContext) -> bool:
        page = await BrowserManager.new_page(context)
        await page.goto(self.ACCOUNT_URL, wait_until="domcontentloaded")
        await page.wait_for_load_state("networkidle")

        if "login" in page.url.lower():
            logger.warning("Aliyun session expired, re-authentication needed")
            return False
        logger.info("Aliyun session is valid")
        return True
