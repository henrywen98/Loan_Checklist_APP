import os
from pathlib import Path
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# 页面配置
st.set_page_config(page_title="Loan Checklist Generator", page_icon="📝")

# 加载本地 .env（本地开发使用；在 Streamlit Cloud 上用 st.secrets）
load_dotenv()

APP_DIR = Path(__file__).parent
PROMPT_FILE = APP_DIR / "loan_checklist_prompt.md"


def load_api_config():
   """优先从 st.secrets 读取，其次从 .env 读取。"""
   api_key = None
   model = None
   try:
      api_key = st.secrets["openai"]["api_key"]
      model = st.secrets["openai"].get("model")
   except Exception:
      pass

   if not api_key:
      api_key = os.getenv("OPENAI_API_KEY")
   if not model:
      model = os.getenv("OPENAI_MODEL", "gpt-5-mini")

   return api_key, model


def load_prompt() -> str:
   if not PROMPT_FILE.exists():
      st.error(f"Prompt file not found: {PROMPT_FILE}")
      st.stop()
   return PROMPT_FILE.read_text(encoding="utf-8")


def build_prompt(template: str, data: dict) -> str:
   try:
      return template.format(**data)
   except KeyError as e:
      st.error(f"Missing prompt placeholder: {e}")
      st.stop()

# 页面标题
st.title("📝 Loan Document Checklist Generator")
st.markdown("Easily generate a professional loan document checklist based on client information.")

# 读取 API 配置（优先 st.secrets，其次 .env）
api_key, model = load_api_config()
if not api_key:
   st.error("OpenAI API key is missing. Set it in .streamlit/secrets.toml or .env as OPENAI_API_KEY.")
   st.stop()

client = OpenAI(api_key=api_key)

# 表单输入
with st.form("client_form"):
    client_name = st.text_input("Client Name")
    loan_purpose = st.selectbox("Loan Purpose", ["Purchase", "Refinance", "Construction", "Others"])
    employment_type = st.selectbox("Employment Type", ["PAYG", "Self-Employed", "Low Doc"])
    passport_type = st.selectbox("Passport Type", ["Australian", "Non-Australian"])
    rental_property = st.selectbox("Has Rental Properties?", ["Yes", "No"])
    trust_assets = st.selectbox("Has Trust-held Assets?", ["Yes", "No"])
    country = st.selectbox("Current Country of Residence", ["Australia", "Other Country"])
    notes = st.text_area("Additional Notes (Optional)")
    submitted = st.form_submit_button("Generate Checklist")

if submitted:
   # 从文件加载并构造 prompt
   template = load_prompt()
   prompt = build_prompt(
      template,
      dict(
         client_name=client_name,
         loan_purpose=loan_purpose,
         employment_type=employment_type,
         passport_type=passport_type,
         rental_property=rental_property,
         trust_assets=trust_assets,
         country=country,
         notes=notes,
      ),
   )

   with st.spinner("Generating checklist..."):
      response = client.chat.completions.create(
         model=model,
         messages=[
            {"role": "system", "content": "You are an expert mortgage broker assistant."},
            {"role": "user", "content": prompt},
         ],
      )
      checklist = response.choices[0].message.content

   # 输出结果
   st.markdown("### ✅ Checklist Output")
   st.code(checklist, language="markdown")
   st.download_button("Download Checklist", checklist, file_name=f"{client_name}_LoanChecklist.txt")
