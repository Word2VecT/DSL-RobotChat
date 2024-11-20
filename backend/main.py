"""Module that sets up a FastAPI application for a chatbot backend.

It includes configuration for CORS, logging, and defines an endpoint
for processing chat messages using a DSL interpreter.
"""

# main.py
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dsl_interpreter import DSLInterpreter

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 仅允许本地 React 端口访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 定义消息模型
class Message(BaseModel):
    """Schema for user messages.

    This class defines the structure of the message sent to the
    chat endpoint. It contains a single field:
    - text: The user's input message.
    """

    text: str


# 初始化DSL解释器
interpreter = DSLInterpreter(
    dsl_file_path="./rules.dsl",
    grammar_file_path="./dsl_grammar.lark",
)


@app.post("/chat")
async def chat_endpoint(message: Message) -> dict:
    """Handle incoming chat requests and return a reply.

    This endpoint accepts a POST request containing a user message,
    processes it using the DSLInterpreter, and returns a corresponding
    reply.

    Args:
        message (Message): The user message sent as a POST request.

    Returns:
        dict: A dictionary with the reply to the user's message.

    Example:
        Input: {"text": "Hello"}
        Output: {"reply": "Hi! How can I help you?"}

    """
    user_message = message.text.strip()
    if not user_message:
        return {"reply": "请您输入一些内容, 我很乐意帮助您。"}
    # 获取响应
    response = interpreter.get_response(user_message)
    return {"reply": response}
