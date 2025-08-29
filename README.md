# Loan Checklist App

A small Streamlit app that generates a tailored loan document checklist using OpenAI.

## Features
- Easy form to capture client context
- Updated prompt with friendly notes and conditional items
- Outputs a flat numbered checklist with optional prepended guidance for joint applicants

## Project Structure
- `loan_checklist_app.py` — Streamlit app
- `loan_checklist_prompt.md` — Prompt template used to generate the checklist
- `requirements.txt` — Python dependencies
- `.env` — Local-only environment variables (ignored by git)

## Setup
1. Python 3.9+ recommended.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure OpenAI credentials:
   - Local `.env` (development only):
     ```ini
     OPENAI_API_KEY=sk-...  # your real key
     OPENAI_MODEL=gpt-4o-mini
     ```
   - Or in Streamlit Cloud `Secrets`:
     ```toml
     [openai]
     api_key = "sk-..."
     model = "gpt-4o-mini"
     ```

## Run
```bash
streamlit run loan_checklist_app.py
```

## Notes
- The app appends a structured "Client Information" block (including a JSON blob of booleans) to help the model apply [IF ...] conditions from the prompt.
- If your account doesn’t have access to `gpt-4o-mini`, set `OPENAI_MODEL` to a permitted model.
- Keep `.env` out of source control; production deployments should use `st.secrets`.
