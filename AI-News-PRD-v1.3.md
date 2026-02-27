下面是**最终版推送格式规范（带可点击原文链接）**，可直接替换 PRD v1.1 中的推送格式部分。该版本满足：

* 标题
* 内容概要（3行内）
* 来源（**文字超链接跳转原文**）
* 每日5条资讯
* 飞书可直接点击访问原文

这是**最终推荐生产版本格式**。

---

# 最终推送格式规范（带原文链接）

## 1. 每日推送结构

每日推送：

```
5条AI资讯
```

整体格式：

```
🤖 AI行业快讯 | YYYY-MM-DD


1️⃣ 标题

内容概要（最多3行）

来源：来源名称（点击查看原文）


2️⃣ 标题

内容概要（最多3行）

来源：来源名称（点击查看原文）


3️⃣ 标题

内容概要（最多3行）

来源：来源名称（点击查看原文）


4️⃣ 标题

内容概要（最多3行）

来源：来源名称（点击查看原文）


5️⃣ 标题

内容概要（最多3行）

来源：来源名称（点击查看原文）
```

---

# 2. 单条资讯格式（最终版）

每条资讯格式：

```
序号 + 标题

内容概要

来源：可点击链接
```

示例：

```
1️⃣ OpenAI发布新GPT模型

OpenAI推出新一代GPT模型，显著提升上下文长度并降低推理成本，支持复杂Agent任务和长文档分析场景，新模型优化稳定性并逐步向开发者开放API。

来源：OpenAI Blog
https://openai.com/blog/xxxx
```

---

# 3. 飞书链接格式规范（重要）

飞书机器人文本消息支持 URL 自动识别。

因此必须使用：

```
来源：OpenAI Blog
https://openai.com/blog/xxxx
```

而不是：

```
来源：[OpenAI Blog](URL)
```

原因：

* Markdown 在 Feishu text 消息下可能失效
* 纯URL最稳定
* 必定可点击

这是**工程推荐格式**。

---

# 4. AI摘要模块更新

模块：

```
ai_summary.py
```

输出JSON改为：

```
{
"title":"",
"summary":"",
"source_name":"",
"url":""
}
```

---

# 5. 字段定义

## title

要求：

```
≤30字
```

必须包含：

* 公司名
* 产品名或技术名

例如：

```
OpenAI发布新GPT模型
```

---

## summary

要求：

```
80-120字
```

限制：

```
最多3行展示
```

必须说明：

* 哪家公司
* 发布什么
* 新能力
* 应用意义

要求：

```
一段文字
不能换行
```

---

## source_name

示例：

```
OpenAI Blog
```

```
TechCrunch
```

---

## url

示例：

```
https://openai.com/blog/xxx
```

必须是：

```
原文RSS链接
```

不能是：

* 聚合页
* 分类页

---

# 6. AI摘要 Prompt（最终生产版）

固定Prompt：

```
你是AI行业分析师。

总结以下AI新闻。

输出JSON：

{
"title":"",
"summary":"",
"source_name":"",
"url":""
}

要求：

title ≤30字

summary：

80-120字。
最多3行展示完毕。
必须是一段文字。
不能换行。

必须说明：

- 哪家公司
- 发布什么
- 新能力
- 应用价值

source_name：

来源名称。

url：

原文链接。

规则：

必须具体。
避免空话。
避免营销语言。
```

---

# 7. 飞书推送模块（最终版本）

模块：

```
feishu_push.py
```

推送格式：

```
🤖 AI行业快讯 | YYYY-MM-DD


1️⃣ {title}

{summary}

来源：{source_name}
{url}


2️⃣ {title}

{summary}

来源：{source_name}
{url}


3️⃣ {title}

{summary}

来源：{source_name}
{url}


4️⃣ {title}

{summary}

来源：{source_name}
{url}


5️⃣ {title}

{summary}

来源：{source_name}
{url}
```

---

# 8. 示例效果（最终目标）

```
🤖 AI行业快讯 | 2026-02-27


1️⃣ OpenAI发布新GPT模型

OpenAI推出新一代GPT模型，显著提升上下文长度并降低推理成本，支持复杂Agent任务和长文档分析场景，新模型面向开发者逐步开放API并优化稳定性。

来源：OpenAI Blog
https://openai.com/blog/gpt-update


2️⃣ Google升级Gemini模型

Google发布Gemini新版本模型，增强多模态理解能力并支持更复杂推理任务，新版本重点优化API性能并提升响应速度，面向企业开发者开放。

来源：Google Blog
https://blog.google/ai/gemini-update


3️⃣ Meta发布新Llama模型

Meta推出新一代Llama开源模型，提升推理性能并优化多语言支持能力，新模型面向研究人员和开发者开放下载并支持本地部署。

来源：Meta AI
https://ai.meta.com/blog/llama-update


4️⃣ NVIDIA发布推理平台

NVIDIA推出新的AI推理软件平台，优化GPU推理效率并降低部署成本，支持大模型生产环境运行并提升吞吐性能。

来源：NVIDIA Blog
https://developer.nvidia.com/blog/inference


5️⃣ Anthropic升级Claude模型

Anthropic发布Claude新版本模型，增强代码生成能力并提升长上下文稳定性，新模型支持更复杂Agent任务并优化企业应用场景。

来源：Anthropic News
https://anthropic.com/news/claude-update
```

---