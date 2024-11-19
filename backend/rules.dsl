# 初始状态
INIT:
    if contain "hello" reply "您好！请问有什么可以帮助您？"
    if contain "hi" reply "嗨"
    if contain "哈哈" or "嘿嘿" reply "笑啥呢"
    if contain "fu" or "bitch" reply "请文明用语" goto end
    if contain "你好" reply "您好！请问有什么可以帮助您？"
    if contain "价格" reply "我们的产品售价是99美元。" goto price
    else reply "感谢您的使用"

# 价格
price:
    if contain "折扣" reply "我们的产品现在打折，售价是79美元。"
    if contain "优惠" reply "我们的产品现在有优惠活动，售价是79美元。"
    if contain "查询" reply "请问您想查询什么信息？" goto price_search
    if contain "退出价格" reply "感谢您的咨询，请问还有什么可以帮您？"

# 价格查询
price_search:
    if contain "手机" reply "我们的手机售价是99美元。" goto price
    else reply "目前仅能查询手机" goto price

# 结束
end: 
    if contain "拜拜" reply "感谢您的咨询，祝您生活愉快！" goto INIT

# 默认
DEFAULT:
    reply "不能理解，请换种说法。" goto INIT