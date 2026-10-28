
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "student_portal.db"


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                subject TEXT NOT NULL,
                deadline TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending'
            )
        """)


# ---------------- DASHBOARD ----------------

@app.route("/")
def home():
    with get_db() as conn:
        total_tasks = conn.execute(
            "SELECT COUNT(*) FROM tasks"
        ).fetchone()[0]

        completed_tasks = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE status = 'Completed'"
        ).fetchone()[0]

    pending_tasks = total_tasks - completed_tasks

    return render_template(
        "dashboard.html",
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks
    )


# ---------------- ATTENDANCE TRACKER ----------------

@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    result = None
    error = None

    if request.method == "POST":
        try:
            total = int(request.form.get("total_classes", 0))
            attended = int(request.form.get("attended_classes", 0))

            if total <= 0:
                error = "Total classes must be greater than zero."
            elif attended < 0 or attended > total:
                error = "Attended classes must be between 0 and total classes."
            else:
                percentage = attended / total * 100

                result = {
                    "total": total,
                    "attended": attended,
                    "percentage": round(percentage, 2),
                    "warning": percentage < 75
                }

        except ValueError:
            error = "Please enter valid whole numbers."

    return render_template(
        "attendance.html",
        result=result,
        error=error
    )


# ---------------- MARKS TRACKER ----------------

@app.route("/marks", methods=["GET", "POST"])
def marks():
    result = None
    error = None

    if request.method == "POST":
        try:
            subject = request.form.get("subject", "").strip()
            obtained = float(request.form.get("obtained", 0))
            total = float(request.form.get("total", 0))

            if not subject:
                error = "Please enter a subject name."
            elif total <= 0 or obtained < 0 or obtained > total:
                error = "Please enter valid marks."
            else:
                percentage = obtained / total * 100

                result = {
                    "subject": subject,
                    "obtained": obtained,
                    "total": total,
                    "percentage": round(percentage, 2),
                    "message": (
                        "Keep practising this subject!"
                        if percentage < 50
                        else "Good progress! Keep it up!"
                    )
                }

        except ValueError:
            error = "Please enter valid numeric marks."

    return render_template(
        "marks.html",
        result=result,
        error=error
    )


# ---------------- STUDY PLANNER ----------------

@app.route("/study-planner", methods=["GET", "POST"])
def study_planner():
    error = None

    if request.method == "POST":
        task = request.form.get("task", "").strip()
        subject = request.form.get("subject", "").strip()
        deadline = request.form.get("deadline", "")

        if task and subject and deadline:
            with get_db() as conn:
                conn.execute(
                    """
                    INSERT INTO tasks (task, subject, deadline)
                    VALUES (?, ?, ?)
                    """,
                    (task, subject, deadline)
                )
        else:
            error = "Please fill in all the fields."

    with get_db() as conn:
        tasks = conn.execute(
            "SELECT * FROM tasks ORDER BY id DESC"
        ).fetchall()

    return render_template(
        "study_planner.html",
        tasks=tasks,
        error=error
    )


# ---------------- COMPLETE TASK ----------------

@app.route("/complete-task/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    with get_db() as conn:
        conn.execute(
            """
            UPDATE tasks
            SET status = 'Completed'
            WHERE id = ?
            """,
            (task_id,)
        )

    return redirect(url_for("study_planner"))


# ---------------- PROGRESS ANALYTICS ----------------

@app.route("/analytics")
def analytics():
    with get_db() as conn:
        total_tasks = conn.execute(
            "SELECT COUNT(*) FROM tasks"
        ).fetchone()[0]

        completed_tasks = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE status = 'Completed'"
        ).fetchone()[0]

    pending_tasks = total_tasks - completed_tasks

    progress = (
        round(completed_tasks / total_tasks * 100)
        if total_tasks > 0
        else 0
    )

    return render_template(
        "analytics.html",
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        progress=progress
    )


# ---------------- SMART RECOMMENDATIONS ----------------

@app.route("/recommendations")
def recommendations():
    with get_db() as conn:
        tasks = conn.execute(
            "SELECT * FROM tasks ORDER BY id DESC"
        ).fetchall()

    pending_tasks = [
        task for task in tasks
        if task["status"] == "Pending"
    ]

    recommendations_list = []

    if not tasks:
        recommendations_list.append({
            "title": "🎯 Create Your First Study Task",
            "reason": "Your Study Planner has no tasks yet.",
            "action": "Add a subject, task and deadline."
        })

    if pending_tasks:
        recommendations_list.append({
            "title": "📅 Focus on Pending Tasks",
            "reason": f"You have {len(pending_tasks)} pending task(s).",
            "action": "Choose one task and study it for 25 minutes."
        })

        recommendations_list.append({
            "title": "⏱️ Build a Study Routine",
            "reason": "Regular study sessions can help you stay on track.",
            "action": "Study for 25 minutes, then take a 5-minute break."
        })

    if tasks and not pending_tasks:
        recommendations_list.append({
            "title": "🌟 Great Work!",
            "reason": "You have completed all your current study tasks.",
            "action": "Add your next learning goal."
        })

    return render_template(
        "recommendations.html",
        recommendations=recommendations_list
    )


# ---------------- START APPLICATION ----------------

if __name__ == "__main__":
    init_db()
    app.run(debug=True)











