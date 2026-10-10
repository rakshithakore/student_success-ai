from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, csv
ROOT=os.path.dirname(os.path.abspath(__file__)); DB=os.path.join(ROOT,'student_success.db')
app=Flask(__name__); app.secret_key=os.environ.get('STUDENT_SUCCESS_SECRET','change-this-demo-secret')
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init_db():
 with db() as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT UNIQUE,password_hash TEXT,role TEXT,student_id TEXT,display_name TEXT); CREATE TABLE IF NOT EXISTS students(student_id TEXT PRIMARY KEY,student_name TEXT,department TEXT,attendance_pct REAL DEFAULT 0,average_marks REAL DEFAULT 0,skills_score REAL DEFAULT 0,backlogs INTEGER DEFAULT 0,projects INTEGER DEFAULT 0,internships INTEGER DEFAULT 0,courses INTEGER DEFAULT 0,certifications INTEGER DEFAULT 0,linkedin_url TEXT DEFAULT '',github_url TEXT DEFAULT '',exam_percentage REAL DEFAULT 0); CREATE TABLE IF NOT EXISTS subjects(id INTEGER PRIMARY KEY,student_id TEXT,subject TEXT,marks REAL,semester TEXT,backlog_status TEXT); CREATE TABLE IF NOT EXISTS activities(id INTEGER PRIMARY KEY,student_id TEXT,category TEXT,title TEXT,status TEXT,details TEXT);''')
  if not c.execute('SELECT 1 FROM students LIMIT 1').fetchone():
   c.executemany('INSERT INTO students VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',[
   ('STU0001','Aarav Kumar','CSE',92,86,82,0,2,1,3,2,'https://www.linkedin.com/','https://github.com/',86),('STU0002','Diya Reddy','AI-DS',58,48,45,2,0,0,1,0,'','',48),('STU0003','Ishaan Verma','ECE',73,64,61,1,1,0,2,1,'https://www.linkedin.com/','',64),('STU0004','Meera Shah','AI-DS',84,77,74,0,2,1,3,2,'https://www.linkedin.com/','https://github.com/',77),('STU0005','Rohan Patel','IT',49,42,38,3,0,0,0,0,'','',42)])
   c.executemany('INSERT INTO subjects(student_id,subject,marks,semester,backlog_status) VALUES(?,?,?,?,?)', [('STU0001','Data Structures',92,'Sem 3','Cleared'),('STU0001','DBMS',88,'Sem 3','Cleared'),('STU0001','Python',95,'Sem 3','Cleared'),('STU0002','Data Structures',44,'Sem 3','Pending'),('STU0002','Statistics',39,'Sem 3','Pending'),('STU0003','Networks',48,'Sem 3','Pending'),('STU0004','Python',91,'Sem 3','Cleared'),('STU0005','Operating Systems',35,'Sem 3','Pending')])
   c.executemany('INSERT INTO activities(student_id,category,title,status,details) VALUES(?,?,?,?,?)',[('STU0001','Project','Online Outpass','Completed','Flask, Python, SQLite'),('STU0001','Project','Student Success Dashboard','Completed','Python and web app'),('STU0001','Internship','Software Developer Intern','Completed','Demo record'),('STU0001','Course','Python for Data Science','Completed','Online course'),('STU0001','Certification','SQL Fundamentals','Completed','Demo record'),('STU0002','Course','Python Basics','In Progress','Practice recommended'),('STU0003','Project','IoT Attendance Monitor','In Progress','Demo record'),('STU0004','Project','Student Performance Analysis','Completed','Python, Pandas'),('STU0004','Internship','Data Analyst Intern','Completed','Demo record'),('STU0004','Course','Machine Learning','Completed','Online course')])
  for u,p,r,s,n in [('admin','admin123','admin',None,'Administrator'),('staff','staff123','staff',None,'Faculty Member'),('student','student123','student','STU0001','Aarav Kumar'),('parent','parent123','parent','STU0001',"Aarav Kumar's Parent")]:
   if not c.execute('SELECT id FROM users WHERE username=?',(u,)).fetchone(): c.execute('INSERT INTO users(username,password_hash,role,student_id,display_name) VALUES(?,?,?,?,?)',(u,generate_password_hash(p),r,s,n))
def who():
 if not session.get('uid'): return None
 with db() as c: return c.execute('SELECT * FROM users WHERE id=?',(session['uid'],)).fetchone()
def list_students(u):
 with db() as c: return c.execute('SELECT * FROM students ORDER BY student_name').fetchall() if u['role'] in ('admin','staff') else c.execute('SELECT * FROM students WHERE student_id=?',(u['student_id'],)).fetchall()
def get_detail(sid):
 with db() as c: return (c.execute('SELECT * FROM students WHERE student_id=?',(sid,)).fetchone(),c.execute('SELECT * FROM subjects WHERE student_id=?',(sid,)).fetchall(),c.execute('SELECT * FROM activities WHERE student_id=? ORDER BY category',(sid,)).fetchall())
def analyze(s):
 improvements=[]
 if s['attendance_pct']<75: improvements.append('Improve attendance and regular participation')
 if s['average_marks']<65: improvements.append('Strengthen subject fundamentals and exam preparation')
 if s['backlogs']: improvements.append('Make a faculty-approved plan to clear backlogs')
 if s['projects']<2: improvements.append('Build 1–2 practical projects and document them on GitHub')
 if s['internships']<1: improvements.append('Apply for internships or supervised practical experience')
 if s['skills_score']<65: improvements.append('Practice role-specific skills and coding problems')
 if not s['linkedin_url']: improvements.append('Create a professional LinkedIn profile')
 if not s['github_url']: improvements.append('Publish projects on GitHub')
 if not improvements: improvements=['Keep building projects and preparing for interviews']
 score=max(0,min(100,round(.25*s['average_marks']+.2*s['skills_score']+.15*s['attendance_pct']+.15*min(s['projects']*35,100)+.1*min(s['internships']*70,100)+.075*(100 if s['github_url'] else 20)+.075*(100 if s['linkedin_url'] else 20)-min(s['backlogs']*5,20))))
 strengths=[]
 for cond,msg in [(s['average_marks']>=75,'Strong academic performance'),(s['skills_score']>=70,'Good technical skills score'),(s['projects']>=2,'Multiple projects recorded'),(s['internships']>0,'Internship experience recorded'),(bool(s['github_url']),'GitHub profile provided'),(bool(s['linkedin_url']),'LinkedIn profile provided')]:
  if cond: strengths.append(msg)
 return {'score':score,'status':'Promising profile' if score>=75 else ('Developing — targeted preparation recommended' if score>=55 else 'Needs additional support'),'strengths':strengths or ['Build a stronger evidence-backed profile'],'improvements':improvements}
@app.route('/')
def home(): return redirect(url_for('dashboard') if who() else url_for('login'))
@app.route('/login',methods=['GET','POST'])
def login():
 if request.method=='POST':
  with db() as c: u=c.execute('SELECT * FROM users WHERE username=?',(request.form.get('username','').strip(),)).fetchone()
  if u and check_password_hash(u['password_hash'],request.form.get('password','')): session.clear(); session['uid']=u['id']; return redirect(url_for('dashboard'))
  flash('Incorrect username or password.','error')
 return render_template('login.html')
@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))
@app.route('/dashboard')
def dashboard():
 u=who()
 if not u:return redirect(url_for('login'))
 ss=list_students(u); avg=round(sum(s['average_marks'] for s in ss)/len(ss),1) if ss else 0
 return render_template('dashboard.html',user=u,students=ss,average=avg,projects=sum(s['projects'] for s in ss),internships=sum(s['internships'] for s in ss),backlogs=sum(s['backlogs'] for s in ss))
@app.route('/student/<sid>')
def student(sid):
 u=who()
 if not u:return redirect(url_for('login'))
 if u['role'] not in ('admin','staff') and u['student_id']!=sid: flash('You can only view your linked student account.','error'); return redirect(url_for('dashboard'))
 s,subjects,activities=get_detail(sid)
 if not s: flash('Student not found.','error'); return redirect(url_for('dashboard'))
 return render_template('student.html',user=u,s=s,subjects=subjects,activities=activities,ai=analyze(s))
@app.route('/ai',methods=['GET','POST'])
def ai():
 u=who()
 if not u:return redirect(url_for('login'))
 ss=list_students(u); chosen=None; answer=''; question=''
 if request.method=='POST':
  question=request.form.get('question','').strip(); sid=request.form.get('student_id','') if u['role'] in ('admin','staff') else u['student_id']; chosen,subjects,activities=get_detail(sid)
  if chosen:
   a=analyze(chosen); q=question.lower()
   if any(w in q for w in ('job','suitable','hire','fit','placement','role')): answer=f"Readiness estimate: {a['score']}/100 ({a['status']}). Strengths: {', '.join(a['strengths'])}. Improve: {', '.join(a['improvements'])}. This is guidance, not a hiring decision."
   elif any(w in q for w in ('improve','weak','recommend','next','better')): answer='Suggested improvement plan: '+'; '.join(a['improvements'])+'. Review progress with a faculty mentor.'
   else: answer=f"{chosen['student_name']} ({chosen['student_id']}, {chosen['department']}): exam {chosen['exam_percentage']}%, average marks {chosen['average_marks']}%, attendance {chosen['attendance_pct']}%, backlogs {chosen['backlogs']}, projects {chosen['projects']}, internships {chosen['internships']}, courses {chosen['courses']}, certifications {chosen['certifications']}. LinkedIn: {chosen['linkedin_url'] or 'Not provided'}. GitHub: {chosen['github_url'] or 'Not provided'}. Readiness estimate: {a['score']}/100. Improve: {', '.join(a['improvements'])}."
 return render_template('ai.html',user=u,students=ss,chosen=chosen,answer=answer,question=question)
@app.route('/upload',methods=['GET','POST'])
def upload():
 u=who()
 if not u:return redirect(url_for('login'))
 if u['role']!='admin': flash('Only admins can upload CSV.','error'); return redirect(url_for('dashboard'))
 message=''
 if request.method=='POST':
  f=request.files.get('file')
  try:
   if not f or not f.filename.lower().endswith('.csv'): raise ValueError('Choose a CSV file.')
   rows=list(csv.DictReader(f.stream.read().decode('utf-8-sig').splitlines()))
   if not rows or not {'student_id','student_name','department'}.issubset(rows[0]): raise ValueError('Required columns: student_id, student_name, department.')
   nums=['attendance_pct','average_marks','skills_score','backlogs','projects','internships','courses','certifications','exam_percentage']
   with db() as c:
    for r in rows:
     if not r.get('student_id') or not r.get('student_name'): continue
     vals=[r.get(k,'') for k in ['student_id','student_name','department']]+[float(r.get(k) or 0) for k in nums]+[r.get('linkedin_url',''),r.get('github_url','')]
     c.execute('''INSERT INTO students(student_id,student_name,department,attendance_pct,average_marks,skills_score,backlogs,projects,internships,courses,certifications,exam_percentage,linkedin_url,github_url) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(student_id) DO UPDATE SET student_name=excluded.student_name,department=excluded.department,attendance_pct=excluded.attendance_pct,average_marks=excluded.average_marks,skills_score=excluded.skills_score,backlogs=excluded.backlogs,projects=excluded.projects,internships=excluded.internships,courses=excluded.courses,certifications=excluded.certifications,exam_percentage=excluded.exam_percentage,linkedin_url=excluded.linkedin_url,github_url=excluded.github_url''',vals)
   message=f'Imported or updated {len(rows)} rows.'
  except Exception as e: flash('CSV import error: '+str(e),'error')
 return render_template('upload.html',user=u,message=message)
@app.route('/settings',methods=['GET','POST'])
def settings():
 u=who()
 if not u:return redirect(url_for('login'))
 if u['role'] not in ('admin','staff'): flash('Settings are available to staff/admin.'); return redirect(url_for('dashboard'))
 if request.method=='POST':
  name=request.form.get('username','').strip(); pw=request.form.get('password','')
  try:
   with db() as c:
    if pw:c.execute('UPDATE users SET username=?,password_hash=? WHERE id=?',(name,generate_password_hash(pw),u['id']))
    else:c.execute('UPDATE users SET username=? WHERE id=?',(name,u['id']))
   session.clear(); flash('Updated. Please log in again.','success'); return redirect(url_for('login'))
  except sqlite3.IntegrityError: flash('Username already exists.','error')
 return render_template('settings.html',user=u)
if __name__=='__main__': init_db(); app.run(debug=True)
