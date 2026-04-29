# Multi-Agent Ticket System 🤖🎫

一个基于大型语言模型（LLM）的多 Agent 协同客户支持与工单流转系统演示。

## 架构说明
- **Intent Agent**: 负责分析用户意图与情绪，输出结构化 JSON 控制业务流转。
- **RAG Agent**: 检索内部知识库，自动回复常规问题 (FAQ/Tech/Billing)。
- **Routing Agent**: 识别复杂或高情绪负荷问题，自动拦截并生成标准化内部工单交由人工处理。

## 快速开始
1. 克隆仓库
2. 安装依赖：`pip install -r requirements.txt`
3. 复制 `.env.example` 为 `.env` 并填入你的 Gemini API Key。
4. 运行测试：`python main.py`