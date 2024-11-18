rule greet:
    pattern: "hello" | "hi" | "hey"
    response: "您好！有什么可以帮您的吗？"

rule help:
    pattern: "帮助" | "支持" | "需要帮助"
    response: "当然，我在这里帮助您。您需要什么帮助？"

rule farewell:
    pattern: "再见" | "拜拜" | "退出"
    response: "再见！祝您有美好的一天！"

rule default:
    pattern: "*"
    response: "抱歉，我不太明白您的意思。您能换种说法吗？"
