# 客服机器人 DSL 语法说明文档

本说明文档旨在详细描述客服机器人 DSL (领域专用语言) 的语法规则及其功能。通过此 DSL，您可以定义多种状态机规则，帮助机器人根据用户输入提供相应的回复和行为。

---

## **语法结构**

### **1. 基础组成**

DSL 由多个状态 (`state`) 和规则 (`rule`) 组成，每个状态包含一组指令，描述在该状态下的用户输入处理逻辑。  
语法的顶层定义如下：

```yaml
start: rule+
```

- **rule**：由一个状态及其对应的处理逻辑组成。
- **state**：表示机器人的当前状态，标记为状态名 (如 `INIT`, `VARsearch`)。
- **statements**：定义状态下的处理逻辑，包括条件判断、回复和状态迁移。

---

## **保留字状态**

DSL 中存在两个保留字状态：`INIT` 和 `DEFAULT`，必须实现。

- **`INIT`**：
  - 定义机器人初始状态，用户输入会首先匹配 `INIT` 状态中的规则。
  - 如果未定义 `goto`，会默认跳转到 `INIT`。
  
- **`DEFAULT`**：
  - 定义默认回复的状态，当所有状态未能处理用户输入时触发。
  - 在 `DEFAULT` 状态中只能使用 `reply` 指令，不支持其他规则。

---

## **规则语法**

规则包括以下两种形式：

- 条件规则：根据输入内容匹配条件并回复，同时可能发生状态迁移。
- 默认规则：处理未匹配的情况。

### **条件规则**

```yaml
if contain <condition> (or <condition>)* reply <reply_text> ["goto" <next_state>]
```

- **`<condition>`**：要匹配的字符串，例如 `"hello"`。
- **`<reply_text>`**：匹配成功后的回复内容，例如 `"您好！请问有什么可以帮助您？"`。
- **`<next_state>`**（可选）：匹配后跳转的状态。如果未定义 `goto`，缺省跳转到 `INIT`。

示例：

```yaml
if contain "hello" reply "您好！请问有什么可以帮助您？" goto INIT
```

### **默认规则**

```yaml
else reply <reply_text> ["goto" <next_state>]
```

- **`<reply_text>`**：未匹配任何条件时的回复。
- **`<next_state>`**（可选）：执行后跳转的状态。如果未定义 `goto`，缺省跳转到 `INIT`。

**注意**：  

- 一个状态中最多只能定义一个 `else`。
- 如果一个状态未定义 `else`，未匹配的输入会缺省回复 `DEFAULT` 状态中的 `reply`。

示例：

```yaml
else reply "不能理解，请换种说法。" goto INIT
```

### **直接回复规则**

```yaml
reply <reply_text> ["goto" <next_state>]
```

- 直接定义一个回复，无需条件匹配。

示例：

```yaml
reply "感谢您的咨询，请问还有什么可以帮您？" goto INIT
```

---

## **状态声明规则**

每个状态由一个名称 (`state`) 标识，并以冒号 (`:`) 结束，后跟该状态下的逻辑规则：

```yaml
state: NAME
statements: (case)+ default_case? | reply_case
```

- **state**：状态名，例如 `INIT`。
- **statements**：该状态的逻辑处理指令。

### **变量状态**

- 状态名中含有变量（如 `{id}`）时，状态名必须以 `VAR` 开头，例如 `VARsearch`。
- 变量状态通常用于处理动态输入，例如用户查询特定产品或 ID。

示例：

```yaml
VARsearch:
    if contain "{id}" reply "产品{id}的价格为{id.price}" goto INIT
    else reply "请重新输入" goto VARsearch
```

---

## **完整语法定义**

```yaml
start: rule+

rule: state ":" statements

state: NAME

statements: (case)+ default_case? | reply_case

case: "if" "contain" condition (or_condition)* "reply" reply ["goto" next_state]

condition: STRING

or_condition: "or" condition

reply: STRING

next_state: NAME

default_case: "else" "reply" reply ["goto" next_state]

reply_case: "reply" reply ["goto" next_state]
```

---

## **示例说明**

以下为 DSL 示例的功能描述：

1. **初始状态 (`INIT`)**
   - 当用户输入包含特定关键词时，回复不同的内容：
     - 包含 `hello` 或 `你好`，回复友好问候并保持状态。
     - 包含不文明用语 (`fu` 或 `bitch`)，提醒用户文明用语。
   - 若提到 “产品”，提示用户输入产品 ID，并跳转到 `VARsearch` 状态。
   - 若提到 “价格”，回复价格信息并跳转到 `price` 状态。
   - 未定义 `goto` 的规则或未匹配规则，缺省跳转到 `INIT`。

2. **搜索状态 (`VARsearch`)**
   - 用户输入产品 ID（用 `{id}` 表示）时，返回价格信息并返回初始状态。
   - 若输入“退出查询产品”，返回初始状态。
   - 输入未匹配规则时，提示重新输入。

3. **价格状态 (`price`)**
   - 针对折扣和优惠相关查询，提供具体回复。
   - 允许用户退出价格查询或继续深入查询（进入 `price_search` 状态）。

4. **默认状态 (`DEFAULT`)**
   - 未能匹配任何输入时，回复 `DEFAULT` 中的内容。
   - 示例：`reply "不能理解，请换种说法。" goto INIT`

---

## **扩展说明**

- **动态参数处理**：例如 `{id}` 在 `VARsearch` 中表示一个动态参数，可以用于生成定制回复，如 `"产品{id}的价格为{id.price}"`。
- **保留字状态机制**：`INIT` 和 `DEFAULT` 必须实现，未定义规则时提供默认行为，简化 DSL 书写。
- **状态跳转规则**：未定义 `goto` 的规则，缺省跳转到 `INIT`，确保状态逻辑闭环。
