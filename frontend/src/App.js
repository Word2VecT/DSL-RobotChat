// App.js
import React from "react";
import Chat, { Bubble, useMessages } from "@chatui/core";
import "@chatui/core/dist/index.css";
import axios from "axios";

export default function App() {
  const { messages, appendMsg, setTyping } = useMessages([]);

  async function handleSend(type, val) {
    if (type === "text" && val.trim()) {
      // 用户消息
      appendMsg({
        type: "text",
        content: { text: val },
        position: "right"
      });

      setTyping(true); // 显示打字中

      try {
        const response = await axios.post("http://localhost:8000/chat", {
          text: val
        });
        const reply = response.data.reply;

        // 机器人回复
        appendMsg({
          type: "text",
          content: { text: reply }
        });
      } catch (error) {
        console.error("Error:", error);
        appendMsg({
          type: "text",
          content: { text: "无法连接后端，请检查服务是否运行。" }
        });
      } finally {
        setTyping(false); // 隐藏打字中
      }
    }
  }

  function renderMessageContent(msg) {
    const { content } = msg;
    return <Bubble content={content.text} />;
  }

  return (
    <Chat
      navbar={{ title: "智能助理" }}
      messages={messages}
      renderMessageContent={renderMessageContent}
      onSend={handleSend}
    />
  );
}
