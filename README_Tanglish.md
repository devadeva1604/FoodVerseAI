# Food Verse AI — Setup Guide (Tanglish)

Deva, project folder ready. First-time setup-ku indha steps mattum follow pannu.

## 1. Required software
- Python 3.13.7 (already installed)
- Node.js v24.22.0 (already installed)
- Git (already installed)
- VS Code

## 2. Folder open pannradhu
1. ZIP file-a extract pannu.
2. Extract aana `FoodVerseAI` folder-a VS Code-la open pannu.
3. VS Code > Terminal > New Terminal.

## 3. Backend start pannradhu
VS Code terminal-la:
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```
If PowerShell activation blocked:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```
Backend address: http://127.0.0.1:5000

Keep this terminal open.

## 4. Frontend start pannradhu
VS Code-la second terminal open pannu (Terminal > New Terminal), then:
```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```
Open the URL shown in terminal, usually http://localhost:5173.

## 5. Gemini AI enable pannradhu (optional)
1. `backend/.env` file open pannu.
2. `GEMINI_API_KEY=` pakkathula un API key add pannu.
3. Save panni backend terminal-la Ctrl+C, then `python app.py` run pannu.
Without API key, app demo mode-la sample estimates show pannum. Demo results scientific confirmation illa.

## Important
- Food freshness/hygiene results are only visual estimates. AI cannot guarantee food is safe.
- Don't upload private or sensitive images.
- Never upload `.env` or API keys to GitHub.
- If `npm` command has PowerShell issue, use `npm.cmd` exactly as shown.
