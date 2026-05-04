from flask import Flask, render_template, request, redirect, session
import json
import os

app = Flask(__name__)
app.secret_key = "edutrack"

quotes = {
    "Not Started": "Start now. Your future self will thank you.",
    "In Progress": "Keep going. You're doing great.",
    "Done": "Well done! Task completed."
}

# ---------------- USERS ----------------
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return []

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

# ---------------- TASKS ----------------
def load_tasks(username):
    filename = f"{username}_tasks.json"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return []

def save_tasks(username, tasks):
    filename = f"{username}_tasks.json"
    with open(filename, "w") as f:
        json.dump(tasks, f)

# ---------------- SIGN UP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        # check if user exists
        for user in users:
            if user["username"] == username:
                return "Username already exists"

        users.append({
            "username": username,
            "password": password
        })

        save_users(users)
        return redirect("/")

    return render_template("signup.html")

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        for user in users:
            if user["username"] == username and user["password"] == password:
                session["user"] = username
                return redirect("/home")

        return "Wrong login"

    return render_template("login.html")

# ---------------- HOME ----------------
@app.route("/home", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect("/")

    username = session["user"]
    tasks = load_tasks(username)

    if request.method == "POST":
        task = request.form["task"]
        date = request.form["date"]
        time = request.form["time"]
        status = request.form["status"]

        tasks.append({
            "task": task,
            "deadline": f"{date} {time}",
            "status": status,
            "quote": quotes[status]
        })

        save_tasks(username, tasks)
        return redirect("/home")

    return render_template("index.html", tasks=tasks)

# ---------------- UPDATE STATUS ----------------
@app.route("/update_status/<int:index>", methods=["POST"])
def update_status(index):
    username = session["user"]
    tasks = load_tasks(username)

    if 0 <= index < len(tasks):
        new_status = request.form["status"]
        tasks[index]["status"] = new_status
        tasks[index]["quote"] = quotes[new_status]

        save_tasks(username, tasks)

    return redirect("/home")

# ---------------- DELETE ----------------
@app.route("/delete/<int:index>")
def delete(index):
    username = session["user"]
    tasks = load_tasks(username)

    if 0 <= index < len(tasks):
        tasks.pop(index)
        save_tasks(username, tasks)

    return redirect("/home")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
