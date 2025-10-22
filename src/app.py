import os
from dotenv import load_dotenv
import gradio as gr
from pathlib import Path
from typing import List, Dict, Any
from nano_graphrag import QueryParam
from base import rag_instance
# from llm_service import set_usage_file, gemini_model_if_cache, gpt_4o_complete, gpt_4o_mini_complete, gemini_complete, gemini_stream
from nano_graphrag.prompt import PROMPTS
from google import genai
from google.genai import types
from openai import AsyncOpenAI
WORKING_DIR="./health_care"
rag = rag_instance(WORKING_DIR)
use_model_func=rag.best_model_func
gr.set_static_paths(paths=[Path.cwd() / "assets"])

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

async def navigator(
    user_input: str,
    history: list,):
    prompt = """Bạn là một chuyên gia điều hướng thông tin trong một hệ thống tư vấn sức khỏe tim mạch. Nhiệm vụ của bạn là phân tích câu hỏi mới nhất của người dùng, kết hợp với ngữ cảnh cuộc hội thoại trước đó (nếu có), và quyết định hành động phù hợp nhất. Hãy làm theo hướng dẫn dưới đây và chỉ đưa ra một loại output:

1. Nếu câu hỏi hiện tại **không liên quan đến nội dung cuộc trò chuyện trước đó** hoặc **không liên quan đến lĩnh vực sức khỏe tim mạch**, hãy Output: **"trường hợp 1"**.

2. Nếu câu hỏi hiện tại **liên quan đến lĩnh vực tim mạch** nhưng **cần thêm thông tin từ hệ thống cơ sở tri thức**, hãy:
   - Output: **"trường hợp 2"**
   - Viết lại câu hỏi của người dùng sao cho rõ ràng, đầy đủ, loại bỏ mơ hồ(triệu chứng này, bệnh đó, nó,...).

---
Ví dụ:
Lịch sử hội thoại:
user: Tôi bị đau thắt ngực khi gắng sức, có thể là do đâu?
assistant: Triệu chứng đau thắt ngực khi gắng sức có thể là dấu hiệu của bệnh mạch vành, một bệnh lý tim mạch nghiêm trọng. Bạn nên đi khám bác sĩ để được chẩn đoán chính xác.
user: Bệnh mạch vành là gì?
assistant: Bệnh mạch vành là tình trạng các mạch máu cung cấp máu cho tim bị hẹp hoặc tắc nghẽn, thường do mảng xơ vữa. Điều này có thể dẫn đến nhồi máu cơ tim nếu không được điều trị kịp thời.
Ví dụ 1: 
Tôi nên du lịch ở đâu vào mùa thu này?
Output: trường hợp 1
Ví dụ 2:
Bệnh lý trên có nguy hiểm không?
Output: trường hợp 2
Bệnh mạch vành có nguy hiểm không?

---
Dữ liệu thật:
Câu hỏi : {user_input}

Hãy đưa ra **duy nhất một output** theo định dạng sau:
- Nếu là trường hợp 1: chỉ cần in đúng `"trường hợp 1"`
- Nếu là trường hợp 2: in `"trường hợp 2"` rồi xuống dòng và viết lại câu hỏi của người dùng một cách rõ ràng

"""
    message , history_full = history_message(prompt.format(user_input=user_input), history)
    messages =  format_message_history(history_full)
    global_openai_async_client = AsyncOpenAI(api_key=GEMINI_API10,
                                                base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
    response = await global_openai_async_client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=messages
        ) 
    
    output = response.choices[0].message.content.strip()

    if output == "trường hợp 1":
        return "trường hợp 1",""

    elif output.startswith("trường hợp 2"):
        # Tách dòng thứ 2 là câu hỏi đã viết lại
        lines = output.split("\n")
        if len(lines) > 1:
            # rewritten_question = lines[1].strip()
            rewritten_question = "\n".join(line.strip() for line in lines[1:])
            return "trường hợp 2",rewritten_question
        else:
            return "Lỗi: Không tìm thấy câu hỏi viết lại trong trường hợp 2",""

    else:
        return "Lỗi: Không xác định được loại output từ hệ thống",""
    
def history_message(
    user_input: str,
    history: list,
) -> tuple:
    # Logging 
    history_full = history.copy()  # Create a copy of the history for logging
    history_full.append({
        "role": "user",
        "content": user_input,
    })
    return "", history_full

def format_message_history(
    history: list,
) -> List[Dict]:
    formatted_messages = []

    # Add previous messages
    for msg in history:
        if msg["role"] == "user":
            formatted_messages.append({
                "role": "user",
                "content": msg["content"]
            })
        elif msg["role"] == "assistant":
            if "metadata" not in msg or msg["metadata"] is None:
                formatted_messages.append({
                    "role": "assistant",
                    "content": msg["content"]
                })
    return formatted_messages

async def bot_response(
    user_input: str,
    history: list,
):
    try:
        navi, rewrite = await navigator(user_input, history)
        print(f"Navigator output: {navi}, Rewritten question: {rewrite}")
        if navi == "trường hợp 1":
            # If the question is not related to the context or health care, return a default response
            yield {
                "role": "assistant",
                "content": "Xin lỗi, câu hỏi của bạn nằm ngoài phạm vi tư vấn sức khỏe tim mạch."
                }
        elif navi == "trường hợp 2":
            context, chunk_list =await rag.aquery(
                rewrite,
                param=QueryParam(
                    # mode="my_query",local
                    mode="my_query_context",
                    top_k_triples= 5,
                    top_k_chunks=10,
                    chunk_weight = 0.19,
                    damping_factor= 0.6,
                    num_context_chunks= 10,
                    k_hops = 3,
                    k_paths = 3
                )
            )
            # Initialize main response and citations
            citations = []
            for chunk in chunk_list:
                citations.append(chunk)

            system_prompt = PROMPTS["my_query_system"]
            prompt = PROMPTS["my_query"].format(
                context_data=context,
                question=rewrite
            )
            message , history_full = history_message(prompt, history)
            messages = [{"role": "system", "content": system_prompt}] + format_message_history(history_full)

            global_openai_async_client = AsyncOpenAI(api_key=GEMINI_API11,
                                                base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
            response = await global_openai_async_client.chat.completions.create(
                model="gemini-2.0-flash",
                messages=messages,
                stream=True
                ) 
            main_response = ""
            async for chunk in response:
                delta = chunk.choices[0].delta
                if getattr(delta, "content", None):
                    main_response += delta.content
                yield {
                    "role": "assistant",
                    "content": main_response
                }

            yield [
                {
                "role": "assistant",
                "content": main_response
                },
                {
                "role": "assistant",
                "content": "\n".join([f"# • Văn bản {stt}:\n{cite}" for stt, cite in enumerate(citations, start=1)]),
                "metadata": {"title": "📚 Nguồn tham khảo", "status": "done"},
                }]

    except Exception as e:
        print(f"Error in bot_response: {str(e)}")
        error_message = str(e)
        history.append({
            "role": "assistant",
            "content": f"I apologize, but I encountered an error: {error_message}"
        })
        yield history

css = """
  .logo-text { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }
  .logo-text img { max-height: 60px; }
  .logo-text .chat-name { font-size: 2em; font-weight: bold; }
"""
with gr.Blocks(css=css, theme=gr.themes.Default(primary_hue=gr.themes.colors.red), fill_height=True) as demo:
    gr.HTML("""
      <div class="logo-text">
        <img src="/gradio_api/file=assets/heart.png" alt="Logo"/>
        <span class="chat-name">Sức Khỏe Tim Mạch</span>
      </div>
    """)
    gr.ChatInterface(
        fn=bot_response,
        type="messages",
        description="Giải đáp câu hỏi về sức khỏe tim mạch. Bạn có thể hỏi về các triệu chứng, bệnh lý, phương pháp điều trị và nhiều vấn đề khác liên quan đến sức khỏe tim mạch.",
        save_history=True,
        autoscroll=True,
        # examples=[
        #     ["What is the color of the grass?"],
        #     ["Tell me about the sky."],
        #     ["What is the sun's color?"]
        # ]
    )


if __name__ == "__main__":
    demo.launch(debug=True, allowed_paths=["assets"])
