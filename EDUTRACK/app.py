from flask import Flask, render_template, request, redirect, session
import json
import os
import uuid

app = Flask(__name__)
app.secret_key = "edutrack"

USERNAME = "admin"
PASSWORD = "1234"

quotes = {
    "Not Started": "Start now. Your future self will thank you.",
    "In Progress": "Keep going. You're doing great.",
    "Done": "Well done! Task completed."
}

# ---------------- FILE ----------------

def load_tasks():
    if os.path.exists("tasks.json"):
        with open("tasks.json", "r") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open("tasks.json", "w") as f:
        json.dump(tasks, f)

# ---------------- LOGIN ----------------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["user"] = USERNAME
            return redirect("/home")
        return "Wrong login"
    return render_template("login.html")

# ---------------- HOME ----------------

@app.route("/home", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect("/")

    tasks = load_tasks()

    if request.method == "POST":
        task = request.form["task"]
        date = request.form["date"]
        time = request.form["time"]
        status = request.form["status"]

        tasks.append({
            "id": str(uuid.uuid4()),
            "task": task,
            "deadline": f"{date} {time}",
            "status": status,
            "quote": quotes[status]
        })

        save_tasks(tasks)
        return redirect("/home")

    return render_template("index.html", tasks=tasks)

# ---------------- UPDATE STATUS ----------------

@app.route("/update_status/<task_id>", methods=["POST"])
def update_status(task_id):
    tasks = load_tasks()

    for task in tasks:
        if task["id"] == task_id:
            new_status = request.form["status"]
            task["status"] = new_status
            task["quote"] = quotes[new_status]
            break

    save_tasks(tasks)
    return redirect("/home")

# ---------------- DELETE ----------------

@app.route("/delete/<task_id>")
def delete(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)
    return redirect("/home")

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)
