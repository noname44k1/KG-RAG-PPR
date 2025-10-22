import os
import logging
import json
import numpy as np
import time
import asyncio
from dotenv import load_dotenv
from google import genai
from google.genai import types
from openai import AsyncOpenAI, AsyncAzureOpenAI, APIConnectionError, RateLimitError

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from nano_graphrag.base import BaseKVStorage
from nano_graphrag._utils import compute_args_hash, wrap_embedding_func_with_attrs

load_dotenv(dotenv_path="../.env")
api_key = os.getenv("API_KEY")
GPT_KEY=os.getenv("GPT_KEY")
GPT_VIP_KEY=os.getenv("GPT_VIP_KEY")
GEMINI_KEY=os.getenv("GEMINI_KEY")
GEMINI_API1 = os.getenv("GEMINI_API1")
GEMINI_API2 = os.getenv("GEMINI_API2")
GEMINI_API3 = os.getenv("GEMINI_API3")
GEMINI_API4 = os.getenv("GEMINI_API4")
GEMINI_API5 = os.getenv("GEMINI_API5")
GEMINI_API6 = os.getenv("GEMINI_API6")
GEMINI_API7 = os.getenv("GEMINI_API7")
GEMINI_API8 = os.getenv("GEMINI_API8")
GEMINI_API9 = os.getenv("GEMINI_API9")
GEMINI_API10 = os.getenv("GEMINI_API10")
GEMINI_API11 = os.getenv("GEMINI_API11")
GEMINI_API12 = os.getenv("GEMINI_API12")

# gemini model config
# save function
# Tracking variables
total_tokens_used = 0
total_requests = 0
successful_requests = 0
token_usages = []
start_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
USAGE_FILE = "model_usage.json"
def set_usage_file(file_path):
    global USAGE_FILE
    USAGE_FILE = file_path
def save_model_usage():
    stats = {
        "time": start_time,
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "total_tokens_used": total_tokens_used,
        "requests": token_usages
    }
    with open(USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)

# GEMINI_API_KEY_LIST = [GEMINI_API1, GEMINI_API2, GEMINI_API3, GEMINI_API4, GEMINI_API5, GEMINI_API6]
GEMINI_API_KEY_LIST = [GEMINI_API7, GEMINI_API8, GEMINI_API9, GEMINI_API10, GEMINI_API11, GEMINI_API12]
api_key_index=0
semaphore = asyncio.Semaphore(1)
GEMINI_MODEL = "gemini-2.0-flash"
async def gemini_model_if_cache(
    prompt, system_prompt="", history_messages=[], **kwargs
) -> str:
    global total_tokens_used, total_requests, successful_requests, token_usages
    global api_key_index
    # kv storage
    hashing_kv: BaseKVStorage = kwargs.pop("hashing_kv", None)
    args_hash = compute_args_hash(GEMINI_MODEL, prompt)
    if_cache_return = await hashing_kv.get_by_id(args_hash)
    # if if_cache_return is not None:
    #     return if_cache_return["return"]
    # Retry logic for handling rate limits
    messages=[]
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})
    combined_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
    max_retries = 20
    retry_delay = 30
    async with semaphore: 
        temperature = 0.7
        for attempt in range(max_retries):
            total_requests += 1 
            try:
                client = genai.Client(api_key=GEMINI_API_KEY_LIST[api_key_index])
                response = client.models.generate_content(
                    model=GEMINI_MODEL,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=temperature),
                    contents=combined_prompt
                )

                if response.text:
                    response_text = response.text
                    total = response.usage_metadata.total_token_count
                    total_tokens_used += total
                    token_usages.append({
                        "prompt_tokens": response.usage_metadata.prompt_token_count,
                        "completion_tokens": response.usage_metadata.candidates_token_count,
                        "total_tokens": total
                    })
                                # Append the AI model's response to the conversation history.
                    messages.append(
                    {
                        "role": "model",
                        "content": response_text
                    }
                    )
                    successful_requests += 1
                    save_model_usage()
                    if api_key_index == len(GEMINI_API_KEY_LIST) - 1:
                        api_key_index = 0
                    else: 
                        api_key_index += 1
                    break  
                else:
                    if response.candidates[0].finish_reason==4:
                        temperature = min(temperature + 0.2, 2.0)
                        print("reciting")
                    else:
                        raise Exception("No valid response from Gemini API")
            except Exception as e:
                if "429" in str(e):
                    print(f"api_key_index: {api_key_index}")
                    api_key_index += 1
                    if api_key_index >= len(GEMINI_API_KEY_LIST):
                        api_key_index = 0
                    print(f"Rate limit exceeded. Retrying in {retry_delay} seconds... (Attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(retry_delay)  # Wait before retrying
                else:
                    await asyncio.sleep(retry_delay)
        else:
            raise Exception("Max retries exceeded. Failed to get response.")
    await hashing_kv.upsert({args_hash: {"prompt": prompt,"return": response_text, "model": GEMINI_MODEL}})
    return response_text

global_openai_async_client = None
def get_openai_async_client_instance(api_key):
    global global_openai_async_client
    if global_openai_async_client is None:
        global_openai_async_client = AsyncOpenAI(api_key=api_key,base_url="https://api.yescale.io/v1")
    return global_openai_async_client

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=30),
    retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
)
async def openai_complete_if_cache(
    api_key, model, prompt, system_prompt=None, history_messages=[],**kwargs
) -> str:
    global total_tokens_used, total_requests, successful_requests, token_usages

    openai_async_client = get_openai_async_client_instance(api_key)
    hashing_kv: BaseKVStorage = kwargs.pop("hashing_kv", None)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})
    if hashing_kv is not None:
        args_hash = compute_args_hash(model, messages)
        # if_cache_return = await hashing_kv.get_by_id(args_hash)
        # if if_cache_return is not None:
        #     return if_cache_return["return"]

    total_requests += 1 
    response = await openai_async_client.chat.completions.create(
        model=model, messages=messages, **kwargs
    )
    total = response.usage.total_tokens
    total_tokens_used += total
    token_usages.append({
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": total
    })
    successful_requests += 1
    save_model_usage()
    if hashing_kv is not None:
        await hashing_kv.upsert({args_hash: {"prompt": prompt,"return": response.choices[0].message.content, "model": model}})
        await hashing_kv.index_done_callback()
    return response.choices[0].message.content

async def gpt_4o_complete(
    prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    return await openai_complete_if_cache(
        GPT_KEY,
        "gpt-4o",
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        **kwargs,
    )


async def gpt_4o_mini_complete(
    prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    return await openai_complete_if_cache(
        GPT_KEY,
        "gpt-4o-mini",
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        **kwargs,
    )

async def gemini_complete(
    prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    return await openai_complete_if_cache(
        GEMINI_KEY,
        "gemini-2.0-flash",
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        **kwargs,
    )