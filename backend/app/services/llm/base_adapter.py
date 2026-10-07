"""
LLM适配器基类
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx

from .types import LLMConfig, LLMRequest, LLMResponse, LLMProvider, LLMError


class BaseLLMAdapter(ABC):
    """LLM适配器基类"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        """获取HTTP客户端"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.config.timeout)
        return self._client
    
    @abstractmethod
    async def complete(self, request: LLMRequest) -> LLMResponse:
        """发送请求并获取响应"""
        pass
    
    def get_provider(self) -> LLMProvider:
        """获取提供商名称"""
        return self.config.provider
    
    def get_model(self) -> str:
        """获取模型名称"""
        return self.config.model
    
    async def validate_config(self) -> bool:
        """验证配置是否有效"""
        if not self.config.api_key:
            raise LLMError(
                "Chưa cấu hình API Key",
                self.config.provider
            )
        return True
    
    async def with_timeout(self, coro, timeout_seconds: Optional[int] = None) -> Any:
        """处理超时"""
        timeout = timeout_seconds or self.config.timeout
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise LLMError(
                f"Yêu cầu hết thời gian chờ ({timeout}s)",
                self.config.provider
            )
    
    def handle_error(self, error: Any, context: str = "", api_response: str = None) -> None:
        """处理API错误

        Args:
            error: 原始异常
            context: 错误上下文描述
            api_response: API 服务器返回的原始响应信息
        """
        message = str(error)
        status_code = getattr(error, 'status_code', None)

        # 如果错误本身已经有 api_response，优先使用
        if api_response is None:
            api_response = getattr(error, 'api_response', None)

        # 针对不同错误类型提供更详细的信息
        if "超时" in message or "timeout" in message.lower():
            message = f"Yêu cầu hết thời gian chờ ({self.config.timeout}s). Khuyến nghị:\n" \
                     f"1. Kiểm tra kết nối mạng\n" \
                     f"2. Thử tăng thời gian chờ\n" \
                     f"3. Kiểm tra API endpoint"
        elif any(keyword in message for keyword in ["余额不足", "资源包", "充值", "quota", "insufficient", "balance"]):
            message = "Tài khoản không đủ số dư hoặc đã hết quota. Vui lòng bổ sung hạn mức rồi thử lại"
            status_code = status_code or 402
        elif status_code == 401 or status_code == 403:
            message = "Xác thực API thất bại. Khuyến nghị:\n" \
                     "1. Kiểm tra API Key đã được cấu hình đúng\n" \
                     "2. Xác nhận API Key còn hiệu lực\n" \
                     "3. Kiểm tra API Key có đủ quyền"
        elif status_code == 429:
            message = "API bị giới hạn tần suất. Khuyến nghị:\n" \
                     "1. Chờ một lúc rồi thử lại\n" \
                     "2. Giảm số lượng tác vụ đồng thời\n" \
                     "3. Tăng khoảng thời gian giữa các yêu cầu"
        elif status_code and status_code >= 500:
            message = f"Dịch vụ API gặp lỗi ({status_code}). Khuyến nghị:\n" \
                     "1. Thử lại sau\n" \
                     "2. Kiểm tra trang trạng thái của nhà cung cấp\n" \
                     "3. Thử chuyển sang nhà cung cấp LLM khác"

        full_message = f"{context}: {message}" if context else message

        raise LLMError(
            full_message,
            self.config.provider,
            status_code,
            error,
            api_response=api_response
        )
    
    async def retry(self, fn, max_attempts: int = 3, delay: float = 1.0) -> Any:
        """重试逻辑"""
        last_error = None
        
        for attempt in range(max_attempts):
            try:
                return await fn()
            except Exception as error:
                last_error = error
                status_code = getattr(error, 'status_code', None)
                
                # 如果是4xx错误（客户端错误），不重试
                if status_code and 400 <= status_code < 500:
                    raise error
                
                # 最后一次尝试时不等待
                if attempt < max_attempts - 1:
                    # 指数退避
                    await asyncio.sleep(delay * (2 ** attempt))
        
        raise last_error
    
    def build_headers(self, additional_headers: Dict[str, str] = None) -> Dict[str, str]:
        """构建请求头"""
        headers = {
            "Content-Type": "application/json",
        }
        if additional_headers:
            headers.update(additional_headers)
        if self.config.custom_headers:
            headers.update(self.config.custom_headers)
        return headers
    
    async def close(self):
        """关闭客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None






