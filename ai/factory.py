"""
Factory that returns the right AIProvider instance based on settings,
always falling back to MockProvider if anything about the live
provider is unavailable or misconfigured. This is the single entry
point the rest of the app should use to get an AI provider.
"""
from ai.base import AIProvider
from ai.mock_provider import MockProvider
from config.settings import settings
from utils.logger import log_error


def get_ai_provider() -> AIProvider:
    provider_name = settings.effective_provider()

    if provider_name == "openai":
        try:
            from ai.openai_provider import OpenAIProvider

            return OpenAIProvider()
        except Exception as exc:
            log_error("get_ai_provider(openai)", exc)
            return MockProvider()

    if provider_name == "anthropic":
        try:
            from ai.anthropic_provider import AnthropicProvider

            return AnthropicProvider()
        except Exception as exc:
            log_error("get_ai_provider(anthropic)", exc)
            return MockProvider()

    return MockProvider()
