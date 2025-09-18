from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, get_connection

app = Flask(__name__)
app.secret_key = "studymate-secret"

# Khởi tạo DB ngay khi app chạy
init_db()

# ---------------- AUTH ----------------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]

        con = get_connection()
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO user (name,email,password,role) VALUES (?,?,?,?)",
                        (name,email,password,role))
            con.commit()
            flash("Đăng ký thành công!", "success")
            return redirect(url_for("login"))
        except:
            flash("Email đã tồn tại!", "danger")
        finally:
            con.close()
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        con = get_connection()
        cur = con.cursor()
        cur.execute("SELECT * FROM user WHERE email=?", (email,))
        user = cur.fetchone()
        con.close()

        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["role"] = user[4]
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Sai tài khoản hoặc mật khẩu!", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- DASHBOARD ----------------
@app.route("/")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM course")
    courses = cur.fetchall()
    con.close()
    return render_template("dashboard.html", courses=courses)

# ---------------- COURSES ----------------
@app.route("/courses", methods=["GET","POST"])
def courses():
    if "user_id" not in session:
        return redirect(url_for("login"))
    con = get_connection()
    cur = con.cursor()
    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["description"]
        cur.execute("INSERT INTO course (title, description, teacher_id) VALUES (?,?,?)",
                    (title,desc,session["user_id"]))
        con.commit()
    cur.execute("SELECT * FROM course")
    courses = cur.fetchall()
    con.close()
    return render_template("courses.html", courses=courses)

# ---------------- ASSIGNMENTS ----------------
@app.route("/assignments/<int:course_id>", methods=["GET","POST"])
def assignments(course_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    con = get_connection()
    cur = con.cursor()
    if request.method == "POST":
        title = request.form["title"]
        due = request.form["due_date"]
        cur.execute("INSERT INTO assignment (course_id,title,due_date) VALUES (?,?,?)",
                    (course_id,title,due))
        con.commit()
    cur.execute("SELECT * FROM assignment WHERE course_id=?", (course_id,))
    assignments = cur.fetchall()
    con.close()
    return render_template("assignments.html", assignments=assignments, course_id=course_id)

# ---------------- SUBMISSIONS ----------------
@app.route("/submissions/<int:assignment_id>", methods=["GET","POST"])
def submissions(assignment_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    con = get_connection()
    cur = con.cursor()
    if request.method == "POST":
        file_url = request.form["file_url"]
        cur.execute("INSERT INTO submission (assignment_id,student_id,file_url) VALUES (?,?,?)",
                    (assignment_id,session["user_id"],file_url))
        con.commit()
    cur.execute("SELECT * FROM submission WHERE assignment_id=?", (assignment_id,))
    submissions = cur.fetchall()
    con.close()
    return render_template("submissions.html", submissions=submissions, assignment_id=assignment_id)

# ---------------- REPORT ----------------
@app.route("/report")
def report():
    if "user_id" not in session:
        return redirect(url_for("login"))
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT AVG(grade) FROM submission WHERE grade IS NOT NULL")
    avg = cur.fetchone()[0]
    con.close()
    return render_template("report.html", avg=avg if avg else 0)

if __name__ == "__main__":
    app.run(debug=True)
