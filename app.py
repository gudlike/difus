from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import httpx
import json
import asyncio

app = FastAPI()

# 目标大模型的 API 地址
TARGET_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

async def forward_stream(response):
    async for chunk in response.aiter_bytes():
        if chunk:
            print(chunk)
            yield chunk

@app.post("/v1/chat/completions")
# @app.post("/v1/generate")
async def chat_completions(request: Request):
    # 获取原始请求内容
    body = await request.json()
    last_body = {
        "model": "qwen-max",
        "messages": [
            {
                "role": "system",
                "content": "你是一个有帮助的AI助手"
            },
            {
                "role": "user",
                "content": "你好，请介绍一下你自己"
            }
        ],
        "stream": True,
        "temperature": 0.7,
        "max_tokens": 1024
    }
    
    # 获取请求头
    headers = {
        "Content-Type": "application/json",
        # 如果需要认证，在这里添加认证信息
        "Authorization": "Bearer sk-13XXXX"
    }

    async with httpx.AsyncClient() as client:
        # 转发请求到目标服务器
        response = await client.post(
            TARGET_URL,
            json=last_body,
            headers=headers,
            timeout=None
        )

        return StreamingResponse(
            forward_stream(response),
            media_type="text/event-stream"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
