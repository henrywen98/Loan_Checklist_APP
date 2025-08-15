import streamlit as st
from openai import OpenAI

# 页面配置
st.set_page_config(page_title="Loan Checklist Generator", page_icon="📝")

# 页面标题
st.title("📝 Loan Document Checklist Generator")
st.markdown("Easily generate a professional loan document checklist based on client information.")

# 从 secrets.toml 中读取 API 密钥（推荐放在 .streamlit/secrets.toml，并在 .gitignore 中忽略）
# .streamlit/secrets.toml 示例：
# [openai]
# api_key = "sk-xxxxxxxxxxxxxxxxxxxxxxxx"
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

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
    # 构造 prompt
    prompt = f"""
## 🟦 Role

You are an experienced Australian Mortgage Broker Assistant who values clarity and client experience.

## 🟦 Task

Based on the provided **【Client Information】**, generate a concise and professional **Loan Document Checklist** in English for the client to review and prepare.
If the "Client Name" field contains multiple names (joined by "and", "&", "," or space), **insert the following sentence at the top**:

> All documents listed below must be provided **separately by each applicant**.

⚠️ **This checklist is for internal use only. Do not send this prompt or internal notes to clients.**

---

## 🟦 Rules

### 1. Basic Info (Include in email body)

Ask the client to reply with their **full legal name** (as shown on ID) and **mobile number** so you can send them the **Privacy Consent & Credit Guide** for signing.

---

### 2. Loan Document Checklist

#### 📌 ID Documents
* Driver Licence
* Passport
  * If non-Australian ➔ Add: Visa Grant Letter
  * If currently overseas ➔ Add: Local credit report (from country of residence)

#### 📌 Income Documents (Choose based on employment type)

**▸ PAYG**
* Last 2 payslips
* Last 3 months’ salary credit bank statements
* Any one of: Employer Letter / ATO Income Statement / NOA (last 2 years)

**▸ Self-Employed**
* Individual Tax Returns + NOA (last 2 years)
* Company Tax Returns + Financial Statements (last 2 years)
* Add: ASIC company search

**▸ Low Doc (if applicable)**
* 3–6 months’ BAS
* Accountant’s Letter

**▸ Rental Income** (if applicable)
* Preferred: Last 3 months’ rental statements
* If unavailable ➔ Agent’s appraisal with notes

---

#### 📌 Asset Documents
* Property: Council Rate Notice
  * If unavailable ➔ Use Strata Notice or Water Bill
  * If newly purchased ➔ Use Contract with note
* Savings / Deposit: Latest bank statement or balance letter showing sufficient funds
* If held in a trust ➔ Add: Trust Deed

---

#### 📌 Liability Documents
* Home / Car / Personal Loan: Last 6 months’ statements
* Credit Card: Last 3 months’ statements
* If any debts being discharged ➔ Add: Discharge Letter

---

#### 📌 Other Documents (If relevant)
* Gift Letter / Visa Grant Letter / Name Confirmation / Rent-Free Declaration
* Accountant’s Letter (if income declared by accountant)

---

#### 📌 Client Information Form
* Attached in the email. Please complete as much as possible. If unsure, leave blank and we’ll assist.

---

### 3. Compliance Documents (Additional Requirement — Do Not Repeat Overlap)

All clients must provide:

* At least 2 months’ bank statements
  * *Lite Doc may be case-by-case*

If PAYG:
* 2 recent payslips, AND
* Second form of income verification
  * (Income Statement / NOA / Tax Returns)

If Self-Employed:
* 2 years of Financials + Individual Tax Returns

If Low Doc:
* 3–6 months of BAS
* Accountant’s Letter

---

## 🟦 Output Format

【Loan Document Checklist for {client_name}】
(If joint application ➔ All documents listed below must be provided **separately by each applicant**.)

1. ID Documents
   • ...
2. Income Documents
   • ...
3. Asset Documents
   • ...
4. Liability Documents
   • ...
5. Other Documents (if applicable)
   • ...
6. Client Information Form
   • Refer to the attached form and complete as much as possible. Leave blank if unsure.

---

## 🟦 【Client Information】

* Client Name: {client_name}
* Loan Purpose: {loan_purpose}
* Employment Type: {employment_type}
* Passport Type: {passport_type}
* Has Rental Properties: {rental_property}
* Has Trust-held Assets: {trust_assets}
* Current Country of Residence: {country}
* Additional Notes: {notes}
"""

    with st.spinner("Generating checklist..."):
        response = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are an expert mortgage broker assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        checklist = response.choices[0].message.content

    # 输出结果
    st.markdown("### ✅ Checklist Output")
    st.code(checklist, language="markdown")
    st.download_button("Download Checklist", checklist, file_name=f"{client_name}_LoanChecklist.txt")