from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from playwright.async_api import BrowserContext, Page

from core.browser import BrowserManager
from core.notifier import Notifier
from core.retry import RetryConfig, retry_async

logger = logging.getLogger(__name__)


class PurchaseStatus(Enum):
    SUCCESS = "success"
    SOLD_OUT = "sold_out"
    ERROR = "error"


@dataclass
class PurchaseResult:
    status: PurchaseStatus
    platform: str
    tier: str = ""
    message: str = ""
    error: Optional[Exception] = None


class BaseBuyer(ABC):
    platform_name: str = ""
    purchase_url: str = ""

    def __init__(
        self,
        browser_manager: BrowserManager,
        notifier: Notifier,
        retry_config: Optional[RetryConfig] = None,
    ):
        self.browser_manager = browser_manager
        self.notifier = notifier
        self.retry_config = retry_config or RetryConfig()
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    @abstractmethod
    async def check_login(self, page: Page) -> bool:
        ...

    @abstractmethod
    async def is_available(self, page: Page) -> bool:
        ...

    @abstractmethod
    async def execute_purchase(self, page: Page) -> PurchaseResult:
        ...

    async def pre_warm(self) -> BrowserContext:
        self._context = await self.browser_manager.create_context(
            storage_state_path=self._auth_path()
        )
        self._page = await BrowserManager.new_page(self._context)
        await self._page.goto(self.purchase_url, wait_until="domcontentloaded")
        logger.info(f"[{self.platform_name}] Pre-warmed, current URL: {self._page.url}")
        return self._context

    async def run(self, context: Optional[BrowserContext] = None) -> PurchaseResult:
        if context:
            self._context = context
        if not self._context:
            self._context = await self.browser_manager.create_context(
                storage_state_path=self._auth_path()
            )
        self._page = await BrowserManager.new_page(self._context) if not self._page else self._page

        try:
            logged_in = await self.check_login(self._page)
            if not logged_in:
                msg = f"[{self.platform_name}] Not logged in. Run 'snap-buy login {self.platform_name}' first."
                logger.error(msg)
                self.notifier.failure(self.platform_name, "Not logged in")
                return PurchaseResult(status=PurchaseStatus.ERROR, platform=self.platform_name, message=msg)

            available = await self.is_available(self._page)
            if not available:
                logger.warning(f"[{self.platform_name}] Not available yet, retrying...")

            result = await retry_async(self._purchase_with_retry, config=self.retry_config)
            if result.success:
                self.notifier.success(self.platform_name)
                return PurchaseResult(status=PurchaseStatus.SUCCESS, platform=self.platform_name)
            else:
                self.notifier.failure(self.platform_name, str(result.last_error))
                return PurchaseResult(
                    status=PurchaseStatus.ERROR,
                    platform=self.platform_name,
                    error=result.last_error,
                )
        except Exception as e:
            logger.exception(f"[{self.platform_name}] Unexpected error: {e}")
            await self._take_screenshot("unexpected_error")
            self.notifier.failure(self.platform_name, str(e))
            return PurchaseResult(status=PurchaseStatus.ERROR, platform=self.platform_name, error=e)

    async def _purchase_with_retry(self) -> None:
        result = await self.execute_purchase(self._page)
        if result.status != PurchaseStatus.SUCCESS:
            raise RuntimeError(f"Purchase failed: {result.message}")

    def _auth_path(self) -> Path:
        auth_dir = Path(__file__).resolve().parent.parent / "auth"
        return auth_dir / f"{self.platform_name}_state.json"

    async def _take_screenshot(self, name: str) -> None:
        if self._page:
            logs_dir = Path(__file__).resolve().parent.parent / "logs" / "screenshots"
            logs_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = logs_dir / f"{self.platform_name}_{name}_{timestamp}.png"
            await self._page.screenshot(path=str(path))
            logger.info(f"Screenshot saved: {path}")
