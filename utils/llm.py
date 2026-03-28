from openai import AsyncOpenAI
from functools import wraps

client = AsyncOpenAI()
_total_cost : float = 0.0

# Prices per 1M tokens (USD) — update if model pricing changes
_PRICING = {
    "gpt-4o-mini": {"input": 0.15, "cached_input": 0.075, "output": 0.60},
    "gpt-4o":      {"input": 2.50, "cached_input": 1.25,  "output": 10.00},
    "gpt-5.4-nano":  {"input": 0.2, "cached_input": 0.02,  "output": 1.25}
}

def get_cost() -> float:
    """Returns the total accumulated LLM cost in USD for this session."""
    return _total_cost

def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int, cached_tokens: int = 0) -> float:
    """Returns the estimated cost in USD for a given model and token usage."""
    pricing = next((v for k, v in _PRICING.items() if k in model), None)
    if not pricing:
        raise ValueError(f"No pricing info for model: {model}")
    uncached_tokens = prompt_tokens - cached_tokens
    return (
        uncached_tokens * pricing["input"] +
        cached_tokens   * pricing["cached_input"] +
        completion_tokens * pricing["output"]
    ) / 1_000_000

def _track_cost(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        global _total_cost
        response = await func(*args, **kwargs)
        model = response.model
        cached = response.usage.prompt_tokens_details.cached_tokens if response.usage.prompt_tokens_details else 0
        cost = calculate_cost(model, response.usage.prompt_tokens, response.usage.completion_tokens, cached)
        _total_cost += cost
        return response
    return wrapper

@_track_cost
async def call_llm(prompt: str, system_prompt: str = None, temperature: float = 0, json_schema: dict = None):
    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    messages.append({'role': 'user', 'content': prompt})

    kwargs = {"model": "gpt-4o-mini", "messages": messages, "temperature": temperature}
    if json_schema:
        kwargs["response_format"] = json_schema

    return await client.chat.completions.create(**kwargs)