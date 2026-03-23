from ..agent_utils.provider import LLMConfig

llm = LLMConfig.get_model(
    provider="ollama",
    model="llama3.1:8b",
)


def llm_guardrail(patch: str) -> bool:
    response = llm.invoke(f"""
Evaluate this code patch.

Answer ONLY:
SAFE or UNSAFE

Patch:
{patch}
""")

    return "SAFE" in response.content.upper()