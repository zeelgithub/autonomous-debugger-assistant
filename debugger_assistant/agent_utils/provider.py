from typing import Optional
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel


class LLMConfig:
    """
    Multi-provider LLM factory (Ollama, OpenAI, etc.)
    Runtime configurable for Streamlit UI.
    """

    @staticmethod
    def get_model(
        provider: str,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0,
        max_tokens: Optional[int] = None,
    ) -> BaseChatModel:

        model_id = f"{provider}:{model}"

        kwargs = {
            "temperature": temperature,
        }

        if provider == "openai":
            if api_key:
                kwargs["api_key"] = api_key

        if provider == "ollama":
            kwargs["base_url"] = base_url or "http://localhost:11434"

        return init_chat_model(
            model_id,
            max_tokens=max_tokens,
            **kwargs,
        )