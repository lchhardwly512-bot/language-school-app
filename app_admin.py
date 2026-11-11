import sqlite3
import flet as ft

def init_db():
    conn = sqlite3.connect("school_data.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def main(page: ft.Page):
    init_db()
    page.title = "پنل مدیر - کلاس زبان"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    announcement_input = ft.TextField(label="متن اطلاعیه سراسری برای دانش‌آموزان", multiline=True, width=350, height=100)
    status_text = ft.Text()

    def send_announcement(e):
        text = announcement_input.value.strip()
        if not text:
            status_text.value = "لطفاً متن اطلاعیه را وارد کنید."
            status_text.color = "red"
            page.update()
            return

        conn = sqlite3.connect("school_data.db")
        c = conn.cursor()
        c.execute("INSERT INTO announcements (text) VALUES (?)", (text,))
        conn.commit()
        conn.close()

        announcement_input.value = ""
        status_text.value = "✅ اطلاعیه با موفقیت ارسال شد."
        status_text.color = "green"
        page.update()

    # دریافت اطلاعات کل آموزشگاه
    conn = sqlite3.connect("school_data.db")
    c = conn.cursor()
    c.execute("SELECT name FROM students")
    students = c.fetchall()

    c.execute("SELECT title, deadline FROM homeworks")
    homeworks = c.fetchall()

    c.execute("SELECT student_name, point_type, reason FROM points")
    points = c.fetchall()
    
    c.execute("SELECT text FROM announcements")
    announcements = c.fetchall()
    conn.close()

    # ساخت لیست‌ها
    students_list = ft.Column([ft.Text(f"👤 {s[0]}") for s in students] if students else [ft.Text("هنوز دانش‌آموزی ثبت نشده است.")])
    hw_list = ft.Column([ft.Text(f"📚 {hw[0]} (مهلت: {hw[1]})") for hw in homeworks] if homeworks else [ft.Text("هیچ تکلیفی ثبت نشده است.")])
    ann_list = ft.Column([ft.Text(f"📢 {a[0]}") for a in announcements] if announcements else [ft.Text("هیچ اطلاعیه‌ای ثبت نشده است.")])
    
    points_list = ft.Column()
    if points:
        for pt in points:
            s_name, p_type, reason = pt
            if p_type == "positive":
                points_list.controls.append(ft.Text(f"🟢 {s_name}: امتیاز مثبت ({reason})", color="green"))
            else:
                points_list.controls.append(ft.Text(f"🔴 {s_name}: امتیاز منفی ({reason})", color="red"))
    else:
        points_list.controls.append(ft.Text("امتیازی ثبت نشده است."))

    def refresh_data(e):
        page.clean()
        main(page)

    page.add(
        ft.Text("👑 پنل مدیریت کل - آموزشگاه زبان", size=24, weight=ft.FontWeight.BOLD, color="purple"),
        ft.ElevatedButton("🔄 به‌روزرسانی اطلاعات", on_click=refresh_data),
        ft.Divider(),

        ft.Text("📢 ارسال اطلاعیه جدید", size=18, weight=ft.FontWeight.BOLD),
        announcement_input,
        ft.ElevatedButton("ارسال به همه‌ی دانش‌آموزان", on_click=send_announcement, color="blue"),
        status_text,
        ft.Divider(),

        ft.Text("👥 لیست دانش‌آموزان ثبت‌نام شده:", size=18, weight=ft.FontWeight.BOLD),
        students_list,
        ft.Divider(),

        ft.Text("📋 تکالیف ارائه شده:", size=18, weight=ft.FontWeight.BOLD),
        hw_list,
        ft.Divider(),

        ft.Text("📢 اطلاعیه‌های ارسال شده:", size=18, weight=ft.FontWeight.BOLD),
        ann_list,
        ft.Divider(),

        ft.Text("⭐ گزارش جامع امتیازات کل آموزشگاه:", size=18, weight=ft.FontWeight.BOLD),
        points_list
    )

ft.app(target=main)
