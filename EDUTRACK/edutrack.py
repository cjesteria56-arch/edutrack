import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import Calendar
from datetime import datetime
import json
import os

# ================= LOGIN SYSTEM =================
USERNAME = "admin"
PASSWORD = "1234"

def check_login():
    if user_entry.get() == USERNAME and pass_entry.get() == PASSWORD:
        login_window.destroy()
        open_main_app()
    else:
        messagebox.showerror("Error", "Invalid Username or Password")

login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x200")

tk.Label(login_window, text="Username").pack(pady=5)
user_entry = tk.Entry(login_window)
user_entry.pack()

tk.Label(login_window, text="Password").pack(pady=5)
pass_entry = tk.Entry(login_window, show="*")
pass_entry.pack()

tk.Button(login_window, text="Login", command=check_login).pack(pady=10)

# ================= MAIN APP =================
def open_main_app():
    global app, entry, time_entry, status_var, cal, tree

    app = tk.Tk()
    app.title("📚 EDUTRACK")
    app.geometry("1000x600")

    quotes = {
        "Not Started": "Start now. Your future self will thank you.",
        "In Progress": "Keep going. You're doing great.",
        "Done": "Well done! Another task completed."
    }

    # ================= FUNCTIONS =================
    def add_task():
        task = entry.get()
        date = cal.get_date()
        time_input = time_entry.get()
        status = status_var.get()

        if not task or not time_input:
            messagebox.showwarning("Warning", "Please fill all fields!")
            return

        deadline = f"{date} {time_input}"
        quote = quotes[status]

        tag = get_tag(status)

        tree.insert("", "end", values=(task, deadline, status, quote), tags=(tag,))
        save_tasks()

        entry.delete(0, tk.END)
        time_entry.delete(0, tk.END)

    def delete_task():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a task first!")
            return

        for item in selected:
            tree.delete(item)

        save_tasks()

    def update_status():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a task first!")
            return

        new_status = status_var.get()
        quote = quotes[new_status]
        tag = get_tag(new_status)

        for item in selected:
            values = list(tree.item(item, "values"))
            values[2] = new_status
            values[3] = quote
            tree.item(item, values=values, tags=(tag,))

        save_tasks()

    def upload_image():
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file_path:
            messagebox.showinfo("Image Selected", f"Image: {os.path.basename(file_path)}")

    def share_task():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a task first!")
            return

        values = tree.item(selected[0], "values")
        text = f"Task: {values[0]} | Deadline: {values[1]} | Status: {values[2]}"

        app.clipboard_clear()
        app.clipboard_append(text)
        messagebox.showinfo("Copied", "Task copied to clipboard!")

    def get_tag(status):
        if status == "Not Started":
            return "not_started"
        elif status == "In Progress":
            return "in_progress"
        else:
            return "done"

    def check_deadlines():
        now = datetime.now()

        for item in tree.get_children():
            values = tree.item(item, "values")
            task_name = values[0]
            deadline_str = values[1]

            try:
                deadline = datetime.strptime(deadline_str, "%m/%d/%y %H:%M")
                if now >= deadline:
                    messagebox.showinfo("⏰ Reminder", f"{task_name} is due or overdue!")
            except:
                pass

        app.after(60000, check_deadlines)

    def save_tasks():
        tasks = []
        for item in tree.get_children():
            tasks.append(tree.item(item)["values"])

        with open("tasks.json", "w") as f:
            json.dump(tasks, f)

    def load_tasks():
        try:
            with open("tasks.json", "r") as f:
                tasks = json.load(f)
                for task in tasks:
                    tag = get_tag(task[2])
                    tree.insert("", "end", values=task, tags=(tag,))
        except:
            pass

    # ================= UI =================
    title = tk.Label(app, text="📚 EDUTRACK - Student Task Tracker",
                     font=("Arial", 18, "bold"))
    title.pack(pady=10)

    frame = tk.Frame(app)
    frame.pack(pady=5)

    tk.Label(frame, text="Task").grid(row=0, column=0)
    entry = tk.Entry(frame, width=25)
    entry.grid(row=0, column=1, padx=5)

    tk.Label(frame, text="Time (HH:MM)").grid(row=0, column=2)
    time_entry = tk.Entry(frame, width=10)
    time_entry.grid(row=0, column=3, padx=5)

    tk.Label(frame, text="Status").grid(row=1, column=0)

    status_var = tk.StringVar(value="Not Started")
    status_menu = ttk.Combobox(frame, textvariable=status_var,
                               values=["Not Started", "In Progress", "Done"],
                               state="readonly")
    status_menu.grid(row=1, column=1)

    tk.Label(frame, text="Date").grid(row=1, column=2)
    cal = Calendar(frame)
    cal.grid(row=1, column=3)

    tk.Button(app, text="➕ Add Task", command=add_task).pack(pady=5)

    table_frame = tk.Frame(app)
    table_frame.pack(fill="both", expand=True)

    columns = ("Task", "Deadline", "Status", "Quote")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")

    tree.heading("Task", text="Task")
    tree.heading("Deadline", text="Deadline")
    tree.heading("Status", text="Status")
    tree.heading("Quote", text="Motivation Quote")

    tree.pack(fill="both", expand=True)

    # COLOR TAGS
    tree.tag_configure("not_started", background="lightcoral")
    tree.tag_configure("in_progress", background="orange")
    tree.tag_configure("done", background="lightgreen")

    btn_frame = tk.Frame(app)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="🔄 Update Status", command=update_status).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="🗑 Delete Task", command=delete_task).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="🖼 Upload Image", command=upload_image).grid(row=0, column=2, padx=5)
    tk.Button(btn_frame, text="🔗 Share", command=share_task).grid(row=0, column=3, padx=5)

    load_tasks()
    check_deadlines()

    app.mainloop()

login_window.mainloop()