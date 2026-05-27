import tkinter as tk
from datetime import datetime
from calendar import month_name
from tkcalendar import Calendar


class DatePicker(tk.Frame):
    def _on_click(self, event):
        if not self.enabled:
            return
        self.show()

    def enable(self):
        self.enabled = True
        self.entry.config(state="normal")
        self.btn.config(fg="black", cursor="hand2")

    def disable(self):
        self.enabled = False
        self.entry.config(state="disabled")
        self.btn.config(fg="#999999", cursor="arrow")

    def __init__(self, master=None, initial=None, **kwargs):
        self.enabled = True

        super().__init__(master, **kwargs)

        self.entry = tk.Entry(self, width=12, relief="solid", bd=1)
        self.entry.pack(side="left")

        self.btn = tk.Label(self, text="📅", cursor="hand2")
        self.btn.pack(side="left", padx=4)
        self.btn.bind("<Button-1>", self._on_click)


        if initial:
            self.entry.insert(0, initial)

        self.top = None
        self.mode = "day"
        self.current_date = None
        self.year_base = datetime.now().year
        self._global_handler = None

        self._alpha = 0.0
        self._fade_job = None

    # -------------------------------------------------
    def get_text(self):
        return self.entry.get().strip()

    # -------------------------------------------------
    def show(self):
        if self.top and self.top.winfo_exists():
            self.close()
            return

        try:
            self.current_date = datetime.strptime(self.get_text(), "%Y-%m-%d")
        except:
            self.current_date = datetime.now()

        self.top = tk.Toplevel(self)
        self.top.overrideredirect(True)

        # Posición inicial
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height() + 2
        self.top.geometry(f"+{x}+{y}")

        # Offset relativo a la ventana padre
        root = self.winfo_toplevel()
        self._x_offset = x - root.winfo_rootx()
        self._y_offset = y - root.winfo_rooty()

        self.wrapper = tk.Frame(self.top, bg="white", bd=1, relief="solid")
        self.wrapper.pack()

        self._build_header()
        self._build_body()

        self.top.bind("<Escape>", lambda e: self.close())
        root.bind("<Configure>", self._follow_parent)

        # Click fuera para cerrar
        def global_click(event):
            if not self.top or not self.top.winfo_exists():
                return
            if self._belongs_to_popup(event.widget):
                return
            if event.widget in (self.entry, self.btn):
                return
            self.close()

        def bind_global():
            root.bind_all("<Button-1>", global_click, add="+")
            self._global_handler = global_click

        self.after(50, bind_global)


        # Animación entrada
        self._alpha = 0.85
        self.top.attributes("-alpha", self._alpha)
        self._fade_in()



    # -------------------------------------------------
    def _fade_in(self):
        if not self.top or not self.top.winfo_exists():
            return

        self._alpha += 0.03
        if self._alpha >= 1:
            self.top.attributes("-alpha", 1.0)
            return

        self.top.attributes("-alpha", self._alpha)
        self.after(12, self._fade_in)


    # -------------------------------------------------
    def _follow_parent(self, event=None):
        if not self.top or not self.top.winfo_exists():
            return

        root = self.winfo_toplevel()
        x = root.winfo_rootx() + self._x_offset
        y = root.winfo_rooty() + self._y_offset
        self.top.geometry(f"+{x}+{y}")

    # -------------------------------------------------
    def _build_header(self):
        header = tk.Frame(self.wrapper, bg="white")
        header.pack(fill="x", pady=4)

        self.btn_prev = tk.Label(header, text="<", width=3, cursor="hand2", bg="white")
        self.btn_prev.pack(side="left")
        self.btn_prev.bind("<Button-1>", lambda e: self._navigate(-1))

        self.lbl_title = tk.Label(
            header,
            text="",
            bg="white",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2"
        )
        self.lbl_title.pack(side="left", expand=True)
        self.lbl_title.bind("<Button-1>", lambda e: self._switch_mode())

        self.btn_next = tk.Label(header, text=">", width=3, cursor="hand2", bg="white")
        self.btn_next.pack(side="right")
        self.btn_next.bind("<Button-1>", lambda e: self._navigate(1))

        self._update_title()

    # -------------------------------------------------
    def _build_body(self):
        if hasattr(self, "body"):
            self.body.destroy()

        self.body = tk.Frame(self.wrapper, bg="white")
        self.body.pack(padx=6, pady=6)

        if self.mode == "day":
            self.cal = Calendar(
                self.body,
                year=self.current_date.year,
                month=self.current_date.month,
                day=self.current_date.day,
                selectmode="day",
                date_pattern="yyyy-mm-dd"
            )
            self.cal.pack()
            self.cal.bind("<<CalendarSelected>>", self._select_day)

        elif self.mode == "month":
            for i, m in enumerate(month_name[1:], start=1):
                b = tk.Label(
                    self.body, text=m[:3], width=8, height=2,
                    cursor="hand2", bg="white"
                )
                b.grid(row=(i - 1) // 4, column=(i - 1) % 4, padx=2, pady=2)
                b.bind("<Button-1>", lambda e, mm=i: self._select_month(mm))

        elif self.mode == "year":
            base = self.year_base
            for i in range(12):
                y = base + i
                b = tk.Label(
                    self.body, text=str(y), width=8, height=2,
                    cursor="hand2", bg="white"
                )
                b.grid(row=i // 4, column=i % 4, padx=2, pady=2)
                b.bind("<Button-1>", lambda e, yy=y: self._select_year(yy))

    # -------------------------------------------------
    def _update_title(self):
        if self.mode == "day":
            txt = f"{month_name[self.current_date.month]} - {self.current_date.year}"
        elif self.mode == "month":
            txt = f"{self.current_date.year}"
        else:
            txt = f"{self.year_base} - {self.year_base + 11}"

        self.lbl_title.config(text=txt)

    # -------------------------------------------------
    def _navigate(self, step):
        if self.mode == "day":
            m = self.current_date.month + step
            y = self.current_date.year
            if m < 1:
                m = 12
                y -= 1
            elif m > 12:
                m = 1
                y += 1
            self.current_date = self.current_date.replace(year=y, month=m)

        elif self.mode == "month":
            self.current_date = self.current_date.replace(
                year=self.current_date.year + step
            )

        elif self.mode == "year":
            self.year_base += step * 12

        self._build_body()
        self._update_title()

    # -------------------------------------------------
    def _switch_mode(self):
        if self.mode == "day":
            self.mode = "month"
        elif self.mode == "month":
            self.mode = "year"
        else:
            self.mode = "day"

        self._build_body()
        self._update_title()

    # -------------------------------------------------
    def _select_day(self, event=None):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.cal.get_date())
        self.close()

    def _select_month(self, month):
        self.current_date = self.current_date.replace(month=month)
        self.mode = "day"
        self._build_body()
        self._update_title()
        return "break"

    def _select_year(self, year):
        self.current_date = self.current_date.replace(year=year)
        self.mode = "month"
        self._build_body()
        self._update_title()
        return "break"

    # -------------------------------------------------
    def _belongs_to_popup(self, widget):
        if not hasattr(widget, "master"):
            return False
        while widget:
            if widget == self.top:
                return True
            widget = widget.master
        return False

    # -------------------------------------------------
    def close(self):
        if self._fade_job:
            self.after_cancel(self._fade_job)
            self._fade_job = None
        self._fade_out()

    def _fade_out(self):
        try:
            self.winfo_toplevel().unbind("<Configure>")
        except:
            pass


        if not self.top or not self.top.winfo_exists():
            return

        self._alpha -= 0.06
        if self._alpha <= 0:
            if self._global_handler:
                self.winfo_toplevel().unbind_all("<Button-1>")
                self._global_handler = None
            self.top.destroy()
            self.top = None
            return

        self.top.attributes("-alpha", self._alpha)
        self.after(10, self._fade_out)
