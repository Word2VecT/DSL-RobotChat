import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import App from "./App";

jest.mock("axios", () => ({
  post: jest.fn()
}));

describe("App Component", () => {
  it("renders the Chat component with the navbar title", () => {
    render(<App />);
    expect(screen.getByText("智能客服助手")).toBeInTheDocument();
  });

  it("sends a user message and displays it", () => {
    render(<App />);

    // Select input box and send button
    const input = screen.getByRole("textbox");
    const sendButton = screen.getByRole("button");

    // Type a message and click send
    fireEvent.change(input, { target: { value: "Hello" } });
    fireEvent.click(sendButton);

    // Check if user message is displayed
    expect(screen.getByText("Hello")).toBeInTheDocument();
  });

  it("displays a typing indicator and bot reply when message is sent", async () => {
    const mockReply = "Hi, how can I assist you?";
    const axios = require("axios");
    axios.post.mockResolvedValueOnce({
      data: { reply: mockReply }
    });

    render(<App />);

    // Select input box and send button
    const input = screen.getByRole("textbox");
    const sendButton = screen.getByRole("button");

    // Type a message and click send
    fireEvent.change(input, { target: { value: "Hello" } });
    fireEvent.click(sendButton);

    // Check for typing indicator (initially)
    expect(screen.getByText("显示打字中")).toBeInTheDocument();

    // Wait for the bot's reply
    await screen.findByText(mockReply);

    // Verify bot reply is displayed
    expect(screen.getByText(mockReply)).toBeInTheDocument();
  });

  it("handles errors when the bot cannot reply", async () => {
    const axios = require("axios");
    axios.post.mockRejectedValueOnce(new Error("Network error"));

    render(<App />);

    // Select input box and send button
    const input = screen.getByRole("textbox");
    const sendButton = screen.getByRole("button");

    // Type a message and click send
    fireEvent.change(input, { target: { value: "Hello" } });
    fireEvent.click(sendButton);

    // Wait for the error message
    await screen.findByText("无法连接后端，请检查服务是否运行。");

    // Verify the error message is displayed
    expect(screen.getByText("无法连接后端，请检查服务是否运行。")).toBeInTheDocument();
  });
});
