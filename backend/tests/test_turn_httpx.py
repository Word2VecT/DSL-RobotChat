import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app


@pytest.mark.asyncio
async def test_chat_price():
    """Test price-related interactions via /chat endpoint."""
    transport = ASGITransport(app=app)  # 使用 ASGITransport 替代 app 参数
    async with AsyncClient(transport=transport, base_url="http://localhost:3000") as client:
        # Test price response
        response = await client.post("/chat", json={"text": "价格"})
        assert response.status_code == 200
        assert response.json() == {"reply": "我们的产品售价是99美元。"}

        # Test query response
        response = await client.post("/chat", json={"text": "查询"})
        assert response.status_code == 200
        assert response.json() == {"reply": "请问您想查询什么信息？"}

        # Test invalid query
        response = await client.post("/chat", json={"text": "123"})
        assert response.status_code == 200
        assert response.json() == {"reply": "目前仅能查询手机"}

        # Test valid query
        response = await client.post("/chat", json={"text": "手机"})
        assert response.status_code == 200
        assert response.json() == {"reply": "我们的手机售价是99美元。"}
