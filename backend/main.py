# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dsl_interpreter import DSLInterpreter
import logging

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
    text: str


# 初始化DSL解释器
interpreter = DSLInterpreter("bot_rules.dsl")


@app.post("/chat")
async def chat_endpoint(message: Message):
    user_message = message.text.strip()
    if not user_message:
        return {"reply": "请您输入一些内容，我很乐意帮助您。"}
    # 获取响应
    response = interpreter.get_response(user_message)
    return {"reply": response}
