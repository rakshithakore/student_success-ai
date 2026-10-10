# Student Success AI — starter project

## Run in VS Code on Windows
1. Extract the ZIP and open the extracted folder in VS Code.
2. Terminal → New Terminal.
3. Run:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   py -m pip install -r requirements.txt
   py app.py
   ```
   If activation is blocked, run `py -m pip install -r requirements.txt` and `py app.py` without activating.
4. Open http://127.0.0.1:5000. SQLite data is created automatically.



Admin/staff can see all fictional sample students. Student/parent accounts can only see the linked demo student. Admin can import CSV from Upload CSV.

## CSV fields
Required: `student_id`, `student_name`, `department`. Optional: `attendance_pct`, `average_marks`, `skills_score`, `backlogs`, `projects`, `internships`, `courses`, `certifications`, `linkedin_url`, `github_url`, `exam_percentage`.

## Important limitations
The AI assistant is a transparent rule-based prototype, not a connected LLM or validated job prediction model. Never use its readiness score as the sole basis for hiring, grading, or other high-impact decisions. Before real deployment, replace demo passwords, set a strong `STUDENT_SUCCESS_SECRET`, use HTTPS, add secure parent-child verification, audit logs, backups, password recovery and stronger upload validation, and obtain institutional privacy approval. Do not publish real student data.
