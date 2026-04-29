import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# ==========================================
# 0. 配置环境与初始化 API
# ==========================================
# 加载 .env 文件中的环境变量，防止 API Key 泄露到 GitHub
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("未找到 API Key，请检查 .env 文件配置！")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# ==========================================
# 1. 意图识别 Agent (Intent Recognition Agent)
# ==========================================
def intent_agent(user_input: str) -> dict:
    prompt = f"""
    你是一个意图识别分析师。请分析用户的输入，并返回严格的 JSON 格式。
    不要输出任何其他解释性文本。
    
    分类选项: [FAQ (常见问题), TECH (技术故障), BILLING (财务退款), COMPLAINT (投诉与人工)]
    
    用户输入: "{user_input}"
    
    返回格式要求:
    {{
        "intent": "分类选项",
        "confidence": 0.0到1.0,
        "emotion": "情绪状态",
        "needs_human": boolean
    }}
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"[Intent Agent Error]: {e}")
        return {"intent": "UNKNOWN", "confidence": 0, "needs_human": True}

# ==========================================
# 2. 知识库检索 Agent (RAG Agent / Mock)
# ==========================================
def rag_agent(user_input: str, intent: str) -> str:
    knowledge_base = {
        "FAQ": "我们的工作时间是周一至周五 9:00-18:00。密码重置请点击主页右上角的'忘记密码'。",
        "TECH": "遇到页面白屏或加载失败，请引导用户清除浏览器缓存，或检查系统代理设置。当前服务器状态：全部正常。",
        "BILLING": "退款通常会在 3-5 个工作日内原路返回至支付账户。如果是微信支付，可能会有延迟。"
    }
    context = knowledge_base.get(intent, "抱歉，知识库中暂未找到相关条目。")
    
    prompt = f"""
    你是一个专业的客户支持专家。请基于以下【内部知识库】回答问题。
    如果信息不足，请安抚用户。
    【内部知识库】: {context}
    【用户输入】: {user_input}
    """
    return model.generate_content(prompt).text

# ==========================================
# 3. 路由工单 Agent (Routing & Ticketing Agent)
# ==========================================
def routing_agent(user_input: str, analysis: dict) -> str:
    prompt = f"""
    你是一个工单生成助手。请根据用户的输入和系统分析，生成一份 Markdown 格式的交接工单给人工客服。
    【用户输入】: {user_input}
    【系统分析】: {json.dumps(analysis, ensure_ascii=False)}
    """
    return model.generate_content(prompt).text

# ==========================================
# 4. 中央协调器 (Orchestrator)
# ==========================================
def process_customer_query(user_input: str):
    print(f"\n[{'-'*40}]\n收到用户输入: {user_input}\n正在调度意图识别 Agent...")
    analysis = intent_agent(user_input)
    print(f"-> 意图识别结果: {analysis}")
    
    if analysis.get("needs_human", False) or analysis.get("confidence", 1) < 0.7 or analysis.get("intent") == "COMPLAINT":
        print("\n-> 触发拦截规则，调度路由工单 Agent...\n[生成的内部工单]")
        print(routing_agent(user_input, analysis))
    else:
        print("\n-> 问题在可控范围内，调度知识库 RAG Agent...\n[AI 客服回复]")
        print(rag_agent(user_input, analysis.get("intent")))
    print(f"[{'-'*40}]\n")

if __name__ == "__main__":
    test_1 = "你好，请问怎么重置密码？"
    test_3 = "你们的软件简直是个垃圾！立刻给我转人工，不然我要投诉！"
    
    process_customer_query(test_1)
    process_customer_query(test_3)