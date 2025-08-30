import os
from pathlib import Path
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# 页面配置
st.set_page_config(page_title="Loan Checklist Generator", page_icon="📝")

# 页面标题
st.title("📝 Loan Document Checklist Generator")
st.markdown("Easily generate a professional loan document checklist based on client information.")

# 加载 .env 并根据环境变量选择供应商与模型（deepseek 或 gpt-5-mini）
load_dotenv()

APP_DIR = Path(__file__).parent
PROMPT_FILE = APP_DIR / "loan_checklist_prompt.md"

def load_prompt_template() -> str:
   if not PROMPT_FILE.exists():
      st.error(f"Prompt file not found: {PROMPT_FILE}")
      st.stop()
   return PROMPT_FILE.read_text(encoding="utf-8")

def fill_prompt(template: str, data: dict) -> str:
    # 仅进行定向替换，避免 format 花括号问题
    mapping = {
        "client_name": data.get("client_name", "") or "",
        "loan_purpose": data.get("loan_purpose", "") or "",
        "employment_type": data.get("employment_type", "") or "",
        "passport_type": data.get("passport_type", "") or "",
        "rental_property": data.get("rental_property", "") or "",
        "notes": data.get("notes", "") or "",
    }
    filled = template
    for k, v in mapping.items():
        filled = filled.replace(f"{{{k}}}", str(v))
    return filled

# 默认使用OpenAI
provider = os.getenv("LLM_PROVIDER", "openai").lower()
if provider not in ("openai", "deepseek"):
   provider = "openai"

# 读取模型优先级：通用 LLM_MODEL -> provider-specific env var -> 默认值
common_model = os.getenv("LLM_MODEL")

# 读取通用参数
temperature = float(os.getenv("TEMPERATURE", "0.2"))

if provider == "deepseek":
   api_key = os.getenv("DEEPSEEK_API_KEY")
   model = common_model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
   base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
else:
   api_key = os.getenv("OPENAI_API_KEY")
   model = common_model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
   base_url = os.getenv("OPENAI_BASE_URL") or None

# 兜底：若 .env 未提供，尝试从 st.secrets 读取
if not api_key:
   try:
      if provider == "deepseek":
         api_key = st.secrets.get("deepseek", {}).get("api_key")
      else:
         api_key = st.secrets.get("openai", {}).get("api_key")
   except Exception:
      pass

if not api_key:
   st.error(
      "Missing API key. Set LLM_PROVIDER to 'openai' or 'deepseek' in .env and provide the corresponding API key (OPENAI_API_KEY or DEEPSEEK_API_KEY)."
   )
   st.stop()

client = OpenAI(api_key=api_key, base_url=base_url)

# 显示当前配置信息
with st.expander("🔧 Current Configuration", expanded=False):
    st.write(f"**Provider:** {provider}")
    st.write(f"**Model:** {model}")
    st.write(f"**Temperature:** {temperature}")
    if base_url:
        st.write(f"**Base URL:** {base_url}")
    st.write(f"**API Key:** {'✅ Set' if api_key else '❌ Not Set'}")

# 表单输入
with st.form("client_form"):
    client_name = st.text_input("Client Name")
    loan_purpose = st.selectbox("Loan Purpose", ["Purchase", "Refinance"])
    employment_type = st.selectbox("Employment Type", ["PAYG", "Self-Employed"])
    passport_type = st.selectbox("Passport Type", ["Australian", "Non-Australian"])
    rental_property = st.selectbox("Has Rental Properties?", ["Yes", "No"])
    notes = st.text_area("Additional Notes (Optional)")
    submitted = st.form_submit_button("Generate Checklist")

if submitted:
    # 构造 prompt（从文件读取模板并替换占位符）
    template = load_prompt_template()
    data = {
        "client_name": client_name,
        "loan_purpose": loan_purpose,
        "employment_type": employment_type,
        "passport_type": passport_type,
        "rental_property": rental_property,
        "notes": notes,
    }
    prompt = fill_prompt(template, data)

    with st.spinner("Generating checklist..."):
        # 构建请求参数，从 .env 文件读取配置
        chat_kwargs = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are an expert mortgage broker assistant."},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
        }
            
        response = client.chat.completions.create(**chat_kwargs)

    checklist = response.choices[0].message.content

    # 输出结果
    st.markdown("### ✅ Checklist Output")
    st.code(checklist, language="markdown")
    st.download_button("Download Checklist", checklist, file_name=f"{client_name}_LoanChecklist.txt")