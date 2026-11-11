import sqlite3
import flet as ft

def main(page: ft.Page):
    page.title = "پنل دانش‌آموز - کلاس زبان"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    name_input = ft.TextField(label="نام و نام خانوادگی", width=300)
    pass_input = ft.TextField(label="رمز عبور", password=True, can_reveal_password=True, width=300)
    status_text = ft.Text()

    def open_student_dashboard(student_name):
        page.clean()
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.scroll = ft.ScrollMode.AUTO

        conn = sqlite3.connect("school_data.db")
        c = conn.cursor()

        # ۱. دریافت تکالیف
        c.execute("SELECT title, deadline FROM homeworks")
        homeworks = c.fetchall()

        # ۲. دریافت امتیازات اختصاصی این دانش‌آموز
        c.execute("SELECT point_type, reason FROM points WHERE student_name = ?", (student_name,))
        points = c.fetchall()

        # ۳. دریافت اطلاعیه‌های مدیر
        c.execute("SELECT text FROM announcements")
        announcements = c.fetchall()

        # ۴. دریافت نمرات مستمر این دانش‌آموز
        grades = []
        try:
            c.execute("SELECT score, description FROM continuous_grades WHERE student_name = ?", (student_name,))
            grades = c.fetchall()
        except sqlite3.OperationalError:
            pass
        
        conn.close()

        # محاسبه هوشمند مجموع امتیازات مثبت و منفی
        pos_count = sum(1 for p in points if p[0] == "positive")
        neg_count = sum(1 for p in points if p[0] == "negative")
        total_score = pos_count - neg_count

        # ساخت کارت کارنامه امتیازات
        score_color = "green" if total_score >= 0 else "red"
        score_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📊 وضعیت کل امتیازات کلاسی", weight=ft.FontWeight.BOLD, size=16),
                    ft.Row([
                        ft.Text(f"🟢 مثبت: {pos_count}", color="green", weight=ft.FontWeight.BOLD),
                        ft.Text(f"🔴 منفی: {neg_count}", color="red", weight=ft.FontWeight.BOLD),
                    ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                    ft.Divider(),
                    ft.Text(f"موجودی نهایی امتیاز: {total_score}", weight=ft.FontWeight.BOLD, size=18, color=score_color)
                ]),
                padding=15
            ),
            width=350
        )

        # ساخت لیست نمرات مستمر
        grades_list = ft.Column()
        if grades:
            for g in grades:
                grades_list.controls.append(ft.Card(content=ft.Container(
                    content=ft.Column([
                        ft.Text(f"📝 نمره مستمر: {g[0]}", weight=ft.FontWeight.BOLD, color="blue"),
                        ft.Text(f"💬 توضیحات: {g[1]}", size=13)
                    ]),
                    padding=10
                ), width=350))
        else:
            grades_list.controls.append(ft.Text("هنوز نمره مستمری ثبت نشده است."))

        # ساخت لیست تکالیف
        hw_list = ft.Column()
        if homeworks:
            for hw in homeworks:
                hw_list.controls.append(ft.Card(content=ft.Container(
                    content=ft.Column([
                        ft.Text(f"📚 تکلیف: {hw[0]}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"⏳ مهلت: {hw[1]}", size=12, color="grey")
                    ]),
                    padding=10
                ), width=350))
        else:
            hw_list.controls.append(ft.Text("هیچ تکلیفی ثبت نشده است."))

        # ساخت لیست اطلاعیه‌ها
        ann_list = ft.Column()
        if announcements:
            for ann in announcements:
                ann_list.controls.append(ft.Card(content=ft.Container(
                    content=ft.Text(f"📢 {ann[0]}", color="indigo"),
                    padding=10
                ), width=350))
        else:
            ann_list.controls.append(ft.Text("هیچ اطلاعیه‌ای وجود ندارد."))

        # جزئیات ریز امتیازات
        points_details = ft.Column()
        if points:
            for pt in points:
                p_type, reason = pt
                if p_type == "positive":
                    points_details.controls.append(ft.Text(f"• امتیاز مثبت: {reason}", color="green", size=13))
                else:
                    points_details.controls.append(ft.Text(f"• امتیاز منفی: {reason}", color="red", size=13))
        else:
            points_details.controls.append(ft.Text("سابقه‌ای ثبت نشده است."))

        page.add(
            ft.Text(f"خوش آمدید، {student_name} عزیز! 👋", size=22, weight=ft.FontWeight.BOLD, color="indigo"),
            ft.Divider(),
            
            ft.Text("📢 اطلاعیه‌های مدیریت:", size=16, weight=ft.FontWeight.BOLD),
            ann_list,
            ft.Divider(),

            ft.Text("⭐ کارنامه و وضعیت امتیازات:", size=16, weight=ft.FontWeight.BOLD),
            score_card,
            points_details,
            ft.Divider(),

            ft.Text("📈 نمرات مستمر:", size=16, weight=ft.FontWeight.BOLD),
            grades_list,
            ft.Divider(),

            ft.Text("📋 تکالیف کلاس:", size=16, weight=ft.FontWeight.BOLD),
            hw_list,
            ft.Divider(),

            ft.ElevatedButton("خروج از حساب", on_click=lambda e: main(page), color="red")
        )
        page.update()

    def handle_login(e):
        name = name_input.value.strip()
        password = pass_input.value.strip()

        if not name or not password:
            status_text.value = "لطفاً نام و رمز عبور را وارد کنید."
            status_text.color = "red"
            page.update()
            return

        conn = sqlite3.connect("school_data.db")
        c = conn.cursor()
        c.execute("SELECT password FROM students WHERE name = ?", (name,))
        row = c.fetchone()
        conn.close()

        if row and row[0] == password:
            open_student_dashboard(name)
        else:
            status_text.value = "نام یا رمز نادرست است."
            status_text.color = "red"
            page.update()

    page.add(
        ft.Text("🔐 ورود دانش‌آموز به سامانه", size=22, weight=ft.FontWeight.BOLD),
        name_input,
        pass_input,
        ft.ElevatedButton("ورود به سیستم", on_click=handle_login),
        status_text
    )

ft.app(target=main)
