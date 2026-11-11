import sqlite3
import flet as ft

def init_db():
    conn = sqlite3.connect("school_data.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS homeworks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            deadline TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            point_type TEXT NOT NULL,
            reason TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS continuous_grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            score TEXT NOT NULL,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

def main(page: ft.Page):
    init_db()
    page.title = "پنل معلم - کلاس زبان"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    # --- فیلدهای ثبت‌نام دانش‌آموز ---
    student_name_input = ft.TextField(label="نام و نام خانوادگی دانش‌آموز", width=300)
    student_pass_input = ft.TextField(label="رمز عبور دانش‌آموز", password=True, can_reveal_password=True, width=300)
    student_status = ft.Text()

    def add_student(e):
        name = student_name_input.value.strip()
        password = student_pass_input.value.strip()
        if not name or not password:
            student_status.value = "لطفاً نام و رمز عبور را وارد کنید."
            student_status.color = "red"
            page.update()
            return
        try:
            conn = sqlite3.connect("school_data.db")
            c = conn.cursor()
            c.execute("INSERT INTO students (name, password) VALUES (?, ?)", (name, password))
            conn.commit()
            conn.close()
            student_name_input.value = ""
            student_pass_input.value = ""
            student_status.value = "✅ دانش‌آموز با موفقیت ثبت شد."
            student_status.color = "green"
            page.update()
        except sqlite3.IntegrityError:
            student_status.value = "⚠️ این دانش‌آموز قبلاً ثبت شده است."
            student_status.color = "orange"
            page.update()

    # --- فیلد‌های ثبت تکلیف ---
    hw_title_input = ft.TextField(label="عنوان تکلیف", width=300)
    hw_deadline_input = ft.TextField(label="مهلت انجام (مثلاً: شنبه آینده)", width=300)
    hw_status = ft.Text()

    def add_homework(e):
        title = hw_title_input.value.strip()
        deadline = hw_deadline_input.value.strip()
        if not title or not deadline:
            hw_status.value = "لطفاً عنوان و مهلت تکلیف را وارد کنید."
            hw_status.color = "red"
            page.update()
            return
        conn = sqlite3.connect("school_data.db")
        c = conn.cursor()
        c.execute("INSERT INTO homeworks (title, deadline) VALUES (?, ?)", (title, deadline))
        conn.commit()
        conn.close()
        hw_title_input.value = ""
        hw_deadline_input.value = ""
        hw_status.value = "✅ تکلیف با موفقیت ثبت شد."
        hw_status.color = "green"
        page.update()

    # --- فیلدهای ثبت امتیاز ---
    conn = sqlite3.connect("school_data.db")
    c = conn.cursor()
    c.execute("SELECT name FROM students")
    students_db = [row[0] for row in c.fetchall()]
    conn.close()

    student_dropdown = ft.Dropdown(label="انتخاب دانش‌آموز", options=[ft.dropdown.Option(s) for s in students_db], width=300)
    point_type_dropdown = ft.Dropdown(label="نوع امتیاز", options=[ft.dropdown.Option("positive", "مثبت 🟢"), ft.dropdown.Option("negative", "منفی 🔴")], width=300)
    point_reason_input = ft.TextField(label="دلیل امتیاز (مثلاً: فعالیت کلاسی / بی‌انضباطی)", width=300)
    point_status = ft.Text()

    def add_point(e):
        s_name = student_dropdown.value
        p_type = point_type_dropdown.value
        reason = point_reason_input.value.strip()
        if not s_name or not p_type or not reason:
            point_status.value = "لطفاً تمام فیلدهای امتیاز را پر کنید."
            point_status.color = "red"
            page.update()
            return
        conn = sqlite3.connect("school_data.db")
        c = conn.cursor()
        c.execute("INSERT INTO points (student_name, point_type, reason) VALUES (?, ?, ?)", (s_name, p_type, reason))
        conn.commit()
        conn.close()
        point_reason_input.value = ""
        point_status.value = "✅ امتیاز ثبت شد."
        point_status.color = "green"
        page.update()

    # --- فیلدهای نمره مستمر ---
    grade_student_dropdown = ft.Dropdown(label="انتخاب دانش‌آموز", options=[ft.dropdown.Option(s) for s in students_db], width=300)
    grade_input = ft.TextField(label="نمره (مثلاً 18 یا عالی)", width=300)
    grade_desc_input = ft.TextField(label="توضیحات نمره مستمر", width=300)
    grade_status = ft.Text()

    def add_grade(e):
        s_name = grade_student_dropdown.value
        score = grade_input.value.strip()
        desc = grade_desc_input.value.strip()
        if not s_name or not score:
            grade_status.value = "نام و نمره الزامی است."
            grade_status.color = "red"
            page.update()
            return
        conn = sqlite3.connect("school_data.db")
        c = conn.cursor()
        c.execute("INSERT INTO continuous_grades (student_name, score, description) VALUES (?, ?, ?)", (s_name, score, desc))
        conn.commit()
        conn.close()
        grade_input.value = ""
        grade_desc_input.value = ""
        grade_status.value = "✅ نمره مستمر ثبت شد."
        grade_status.color = "green"
        page.update()

    def refresh_page(e):
        page.clean()
        main(page)

    page.add(
        ft.Text("👩‍🏫 پنل مدیریت معلم - کلاس زبان", size=24, weight=ft.FontWeight.BOLD, color="teal"),
        ft.ElevatedButton("🔄 تازه‌سازی صفحه و لیست‌ها", on_click=refresh_page),
        ft.Divider(),

        ft.Text("👤 ثبت‌نام دانش‌آموز جدید", size=18, weight=ft.FontWeight.BOLD),
        student_name_input,
        student_pass_input,
        ft.ElevatedButton("ثبت دانش‌آموز", on_click=add_student),
        student_status,
        ft.Divider(),

        ft.Text("📚 تعریف تکلیف جدید", size=18, weight=ft.FontWeight.BOLD),
        hw_title_input,
        hw_deadline_input,
        ft.ElevatedButton("ثبت تکلیف", on_click=add_homework),
        hw_status,
        ft.Divider(),

        ft.Text("⭐ ثبت امتیاز مثبت / منفی", size=18, weight=ft.FontWeight.BOLD),
        student_dropdown,
        point_type_dropdown,
        point_reason_input,
        ft.ElevatedButton("ثبت امتیاز", on_click=add_point),
        point_status,
        ft.Divider(),

        ft.Text("📈 ثبت نمره مستمر", size=18, weight=ft.FontWeight.BOLD),
        grade_student_dropdown,
        grade_input,
        grade_desc_input,
        ft.ElevatedButton("ثبت نمره مستمر", on_click=add_grade),
        grade_status,
    )

ft.app(target=main)
