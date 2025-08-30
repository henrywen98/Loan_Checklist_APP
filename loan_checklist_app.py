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

# 加载 .env（仅本地开发使用）
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

def get_config_value(key: str, default_value: str = "") -> str:
    """
    优先级：环境变量 -> Streamlit Secrets -> 默认值
    支持从 config 部分和对应服务商部分读取
    """
    # 1. 从环境变量读取
    env_value = os.getenv(key)
    if env_value:
        return env_value
    
    # 2. 从 Streamlit Secrets 读取
    try:
        # 方式1：从 config 部分读取（您的配置格式）
        if "config" in st.secrets and key in st.secrets["config"]:
            return str(st.secrets["config"][key])
        
        # 方式2：从对应的服务商部分读取
        if key.startswith("DEEPSEEK_") and "deepseek" in st.secrets:
            sub_key = key.replace("DEEPSEEK_", "").lower()
            if sub_key in st.secrets["deepseek"]:
                return str(st.secrets["deepseek"][sub_key])
                
        if key.startswith("OPENAI_") and "openai" in st.secrets:
            sub_key = key.replace("OPENAI_", "").lower()
            if sub_key in st.secrets["openai"]:
                return str(st.secrets["openai"][sub_key])
        
        # 方式3：直接从根级别读取
        if key in st.secrets:
            return str(st.secrets[key])
                
    except Exception:
        pass
    
    return default_value

# 读取配置
provider = get_config_value("LLM_PROVIDER", "openai").lower()
if provider not in ("openai", "deepseek"):
   provider = "openai"

# 读取通用参数
temperature = float(get_config_value("TEMPERATURE", "0.2"))

if provider == "deepseek":
    # DeepSeek 配置
    api_key = get_config_value("DEEPSEEK_API_KEY")
    model = get_config_value("DEEPSEEK_MODEL", "deepseek-chat")
    base_url = get_config_value("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
else:
    # OpenAI 配置
    api_key = get_config_value("OPENAI_API_KEY")
    model = get_config_value("OPENAI_MODEL", "gpt-4o-mini")
    base_url = get_config_value("OPENAI_BASE_URL") or None

if not api_key:
   st.error(
      "Missing API key. Please configure your API keys in Streamlit secrets or environment variables."
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

# 使用说明
st.markdown("---")
with st.expander("📋 How to Use", expanded=False):
    st.markdown("""
    ### Multiple Applicants
    - For **two applicants**, enter names as: `App_1 & App_2`
    - If applicants have **different employment types**, specify in the **Additional Notes** section
    - Example: `App_1 is self-employed and App_2 is PAYG`
    
    ### Tips
    - The system will generate a customized checklist based on your specific inputs
    - Use the Additional Notes field for any special circumstances or requirements
    
    ### Contact
    📧 If you have any questions or suggestions for improvement, please email:  
    [henrywen98@gmail.com](mailto:henrywen98@gmail.com)
    """)

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
        # 构建请求参数
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