import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app


@pytest.mark.asyncio
async def test_chat_endpoint():
    """Test the /chat endpoint."""
    transport = ASGITransport(app=app)  # 使用 ASGITransport 替代 app 参数
    async with AsyncClient(transport=transport, base_url="http://localhost:3000") as client:
        # Test initial greetings
        response = await client.post("/chat", json={"text": "hello"})
        assert response.status_code == 200
        assert response.json() == {"reply": "您好！请问有什么可以帮助您？"}

        response = await client.post("/chat", json={"text": "hi"})
        assert response.status_code == 200
        assert response.json() == {"reply": "嗨"}

        # Test laugh
        response = await client.post("/chat", json={"text": "哈哈"})
        assert response.status_code == 200
        assert response.json() == {"reply": "笑啥呢"}

        response = await client.post("/chat", json={"text": "嘿嘿"})
        assert response.status_code == 200
        assert response.json() == {"reply": "笑啥呢"}

        # Test inappropriate language
        response = await client.post("/chat", json={"text": "fu"})
        assert response.status_code == 200
        assert response.json() == {"reply": "请文明用语"}

        response = await client.post("/chat", json={"text": "bitch"})
        assert response.status_code == 200
        assert response.json() == {"reply": "请文明用语"}

        # Test unknown input
        response = await client.post("/chat", json={"text": "unknown"})
        assert response.status_code == 200
        assert response.json() == {"reply": "不能理解，请换种说法。"}
