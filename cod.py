# 
# ============================================================
# зачётный проект 
#  система учёта сотрудников
# сделал: Мордасов Руслан Игоревич РСОБ 206
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from abc import ABC, abstractmethod
from datetime import datetime
import os


# свой аналог словаря, потому что dict использовать нельзя
# внутри два списка, ищем линейно - для 10 элементов норм
class Map2:
    def __init__(self):
        self._k = []
        self._v = []

    def put(self, key, val):
        if key in self._k:
            idx = self._k.index(key)
            self._v[idx] = val
        else:
            self._k.append(key)
            self._v.append(val)

    def get(self, key, default=None):
        if key in self._k:
            return self._v[self._k.index(key)]
        return default

    def has(self, key):
        return key in self._k

    def keys(self):
        return list(self._k)

    def vals(self):
        return list(self._v)

    def __len__(self):
        return len(self._k)

    def __str__(self):
        out = []
        for i in range(len(self._k)):
            out.append(f"{self._k[i]}:{self._v[i]}")
        return "Map2{" + ", ".join(out) + "}"


# абстрактный класс - база для всех сущностей
class Base(ABC):
    @property
    @abstractmethod
    def uid(self):
        pass

    @abstractmethod
    def info(self):
        pass

    @abstractmethod
    def check(self):
        pass


# класс работника
class Worker(Base):
    def __init__(self, wid, fio, login, pos, age=25):
        self._wid = wid
        self._fio = fio
        self._login = login
        self._pos = pos
        self._age = age
        # на будущее может пригодится
        self._notes = ""
        self._tmp = None

    # геттеры/сеттеры
    @property
    def uid(self):
        return self._wid

    @uid.setter
    def uid(self, v):
        if isinstance(v, int) and v > 0:
            self._wid = v

    @property
    def fio(self):
        return self._fio

    @fio.setter
    def fio(self, v):
        if isinstance(v, str) and len(v) > 0:
            self._fio = v

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, v):
        if isinstance(v, str):
            self._login = v.lower().strip()

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, v):
        if isinstance(v, str):
            self._pos = v

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, v):
        if isinstance(v, int) and 18 <= v <= 100:
            self._age = v

    # спец методы
    def __eq__(self, other):
        if isinstance(other, Worker):
            return self._wid == other._wid
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"Worker(wid={self._wid}, fio='{self._fio}', pos='{self._pos}')"

    def __str__(self):
        return f"[{self._wid}] {self._fio} - {self._pos}"

    def __hash__(self):
        return hash(self._wid)

    # сравнимость
    def __lt__(self, other):
        return self._wid < other._wid

    def __le__(self, other):
        return self._wid <= other._wid

    def __gt__(self, other):
        return self._wid > other._wid

    def __ge__(self, other):
        return self._wid >= other._wid

    # абстрактные
    def info(self):
        return f"Сотрудник {self._fio} ({self._login}) - {self._pos}"

    def check(self):
        return (isinstance(self._wid, int) and
                len(self._fio) > 0 and
                len(self._login) > 0)

    # отладочный метод, потом уберу наверное
    def debug(self):
        return f"Worker {self._wid}: {self._fio}"


# класс задачи
class Job(Base):
    def __init__(self, jid, title, status="new", prio=1):
        self._jid = jid
        self._title = title
        self._status = status
        self._prio = prio

    @property
    def uid(self):
        return self._jid

    @uid.setter
    def uid(self, v):
        if isinstance(v, int) and v > 0:
            self._jid = v

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, v):
        if isinstance(v, str):
            self._title = v

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, v):
        if isinstance(v, str):
            self._status = v

    @property
    def prio(self):
        return self._prio

    @prio.setter
    def prio(self, v):
        if isinstance(v, int) and 1 <= v <= 5:
            self._prio = v

    def __eq__(self, other):
        return self._jid == other._jid if isinstance(other, Job) else False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f"Job(jid={self._jid}, title='{self._title}')"

    def __str__(self):
        return f"Задача #{self._jid}: {self._title} [{self._status}]"

    def __hash__(self):
        return hash(self._jid)

    def __lt__(self, other):
        return self._jid < other._jid

    def __le__(self, other):
        return self._jid <= other._jid

    def __gt__(self, other):
        return self._jid > other._jid

    def __ge__(self, other):
        return self._jid >= other._jid

    def info(self):
        return f"Задача '{self._title}' - {self._status}"

    def check(self):
        return len(self._title) > 0 and self._status in ("new", "progress", "done")


# ============================================================
# переопределённые UI компоненты (10 штук)
# ============================================================

# 1. метка
class Lbl(tk.Label):
    def __init__(self, parent, txt, **kw):
        kw.setdefault("font", ("Arial", 10, "bold"))
        kw.setdefault("fg", "#2c3e50")
        kw.setdefault("anchor", "center")
        super().__init__(parent, text=txt, **kw)


# 2. поле ввода с подсказкой
class Entry2(tk.Entry):
    def __init__(self, parent, hint="", **kw):
        kw.setdefault("width", 30)
        kw.setdefault("font", ("Arial", 10))
        super().__init__(parent, **kw)
        self._hint = hint
        self.insert(0, hint)
        self.bind("<FocusIn>", self._fi)
        self.bind("<FocusOut>", self._fo)

    def _fi(self, ev):
        if self.get() == self._hint:
            self.delete(0, tk.END)

    def _fo(self, ev):
        if not self.get().strip():
            self.insert(0, self._hint)


# 3. кнопка
class Btn(tk.Button):
    def __init__(self, parent, txt, cmd=None, **kw):
        kw.setdefault("bg", "#27ae60")
        kw.setdefault("fg", "white")
        kw.setdefault("font", ("Arial", 10, "bold"))
        kw.setdefault("activebackground", "#1e8449")
        kw.setdefault("activeforeground", "white")
        kw.setdefault("width", 20)
        super().__init__(parent, text=txt, command=cmd, **kw)


# 4. выпадашка - наследуем напрямую от Combobox
class Combo(ttk.Combobox):
    def __init__(self, parent, vals=None, **kw):
        kw.setdefault("width", 25)
        kw.setdefault("state", "readonly")
        super().__init__(parent, **kw)
        if vals:
            self["values"] = vals


# 5. чекбокс
class Check(tk.Checkbutton):
    def __init__(self, parent, txt, var=None, **kw):
        kw.setdefault("font", ("Arial", 10))
        kw.setdefault("anchor", "w")
        super().__init__(parent, text=txt, variable=var, **kw)


# 6. радио
class Radio(tk.Radiobutton):
    def __init__(self, parent, txt, var=None, val=None, **kw):
        kw.setdefault("font", ("Arial", 10))
        kw.setdefault("anchor", "w")
        super().__init__(parent, text=txt, variable=var, value=val, **kw)


# 7. спинбокс - наследуем напрямую
class Spin(tk.Spinbox):
    def __init__(self, parent, fr=1, to=100, **kw):
        kw.setdefault("width", 10)
        kw.setdefault("font", ("Arial", 10))
        super().__init__(parent, from_=fr, to=to, **kw)

    def setVal(self, v):
        self.delete(0, tk.END)
        self.insert(0, str(v))


# 8. прогресс бар
class PBar(ttk.Progressbar):
    def __init__(self, parent, mx=100, **kw):
        kw.setdefault("length", 300)
        kw.setdefault("mode", "determinate")
        super().__init__(parent, maximum=mx, **kw)


# 9. слайдер
class Scale2(tk.Scale):
    def __init__(self, parent, fr=0, to=100, **kw):
        kw.setdefault("orient", tk.HORIZONTAL)
        kw.setdefault("length", 300)
        kw.setdefault("font", ("Arial", 9))
        super().__init__(parent, from_=fr, to=to, **kw)


# 10. текстовое поле
class TxtBox(tk.Text):
    def __init__(self, parent, **kw):
        kw.setdefault("width", 60)
        kw.setdefault("height", 12)
        kw.setdefault("font", ("Consolas", 10))
        kw.setdefault("state", "disabled")
        super().__init__(parent, **kw)

    def add(self, txt):
        self.config(state="normal")
        self.insert(tk.END, txt + "\n")
        self.config(state="disabled")

    def clear(self):
        self.config(state="normal")
        self.delete(1.0, tk.END)
        self.config(state="disabled")


# ============================================================
# главное окно
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Учёт сотрудников - зачёт")
        self.root.geometry("650x700")
        self.root.resizable(False, False)

        # для отчёта
        self._login = "student_user"
        self._uname = "Иванов И.И."
        self._t_in = datetime.now()
        self._t_out = None

        # 10 работников
        self._workers = [
            Worker(1, "Иванов Иван", "ivanov", "Разработчик", 28),
            Worker(2, "Петров Пётр", "petrov", "Дизайнер", 32),
            Worker(3, "Сидоров Сидор", "sidorov", "Менеджер", 40),
            Worker(4, "Смирнова Анна", "smirnova", "Тестировщик", 26),
            Worker(5, "Кузнецов Олег", "kuznetsov", "Аналитик", 35),
            Worker(6, "Попова Мария", "popova", "DevOps", 29),
            Worker(7, "Васильев Дмитрий", "vasilyev", "Архитектор", 42),
            Worker(8, "Соколов Алексей", "sokolov", "Разработчик", 31),
            Worker(9, "Михайлова Елена", "mikhailova", "Дизайнер", 27),
            Worker(10, "Новиков Сергей", "novikov", "Менеджер", 38),
        ]

        # кастомный маппинг
        self._roles = Map2()
        self._roles.put("dev", "Разработчик")
        self._roles.put("design", "Дизайнер")
        self._roles.put("mgr", "Менеджер")
        self._roles.put("qa", "Тестировщик")
        self._roles.put("analyst", "Аналитик")

        self._build()
        self._refresh()

        # закрытие окна
        self.root.protocol("WM_DELETE_WINDOW", self._quit)

    # статические методы
    @staticmethod
    def fmt(dt):
        return dt.strftime("%d.%m.%Y %H:%M:%S")

    @staticmethod
    def report_line(login, t_in, t_out, uname):
        ti = App.fmt(t_in)
        to = App.fmt(t_out)
        return f"| {login} | {ti} | {to} | {uname} | {ti} | {to} |"

    @staticmethod
    def is_ok(w):
        return w.check() if isinstance(w, Worker) else False

    # интерфейс
    def _build(self):
        main = tk.Frame(self.root, padx=15, pady=15)
        main.pack(fill=tk.BOTH, expand=True)

        # заголовок
        self.lbl_title = Lbl(main, txt="Панель управления сотрудниками")
        self.lbl_title.pack(pady=(0, 15))

        # фильтры
        filt = tk.LabelFrame(main, text="Поиск и фильтры", padx=10, pady=10)
        filt.pack(fill=tk.X, pady=5)

        tk.Label(filt, text="Поиск:", font=("Arial", 10)).grid(
            row=0, column=0, sticky="w", pady=3)
        self.ent_search = Entry2(filt, hint="ФИО или логин...")
        self.ent_search.grid(row=0, column=1, pady=3, padx=5)

        tk.Label(filt, text="Роль:", font=("Arial", 10)).grid(
            row=1, column=0, sticky="w", pady=3)
        self.cmb_role = Combo(filt, vals=["Все роли"] + self._roles.vals())
        self.cmb_role.current(0)
        self.cmb_role.grid(row=1, column=1, pady=3, padx=5)

        self.var_act = tk.BooleanVar(value=False)
        self.chk_act = Check(filt, txt="Только валидные", var=self.var_act)
        self.chk_act.grid(row=2, column=0, columnspan=2, sticky="w", pady=3)

        self.var_sort = tk.StringVar(value="id")
        self.rad_id = Radio(filt, txt="По ID", var=self.var_sort, val="id")
        self.rad_name = Radio(filt, txt="По имени", var=self.var_sort, val="name")
        self.rad_id.grid(row=3, column=0, sticky="w", pady=3)
        self.rad_name.grid(row=3, column=1, sticky="w", pady=3)

        tk.Label(filt, text="Лимит:", font=("Arial", 10)).grid(
            row=4, column=0, sticky="w", pady=3)
        self.spn_lim = Spin(filt, fr=1, to=100)
        self.spn_lim.setVal(10)
        self.spn_lim.grid(row=4, column=1, pady=3, padx=5, sticky="w")

        # действия
        act = tk.LabelFrame(main, text="Действия", padx=10, pady=10)
        act.pack(fill=tk.X, pady=10)

        self.btn_all = Btn(act, txt="Показать всех", cmd=self._show_all)
        self.btn_all.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=3)

        self.btn_chk = Btn(act, txt="Проверить", cmd=self._do_check)
        self.btn_chk.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=3)

        self.btn_srt = Btn(act, txt="Сортировать", cmd=self._do_sort)
        self.btn_srt.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=3)

        # индикаторы
        ind = tk.Frame(main)
        ind.pack(fill=tk.X, pady=5)

        tk.Label(ind, text="Статус:", font=("Arial", 10)).pack(anchor="w")
        self.prg = PBar(ind)
        self.prg.pack(fill=tk.X, pady=3)

        tk.Label(ind, text="Громкость:", font=("Arial", 10)).pack(anchor="w")
        self.scl = Scale2(ind, fr=0, to=100)
        self.scl.set(50)
        self.scl.pack(fill=tk.X, pady=3)

        # вывод
        out = tk.LabelFrame(main, text="Результат", padx=10, pady=10)
        out.pack(fill=tk.BOTH, expand=True, pady=5)

        self.txt = TxtBox(out)
        self.txt.pack(fill=tk.BOTH, expand=True)

    # методы объекта
    def _show_all(self):
        self._refresh()
        self.prg["value"] = 100

    def _do_check(self):
        ok = sum(1 for w in self._workers if self.is_ok(w))
        total = len(self._workers)
        pct = int(ok / total * 100) if total > 0 else 0
        self.txt.add("")
        self.txt.add("--- Валидация ---")
        self.txt.add(f"Валидных: {ok} из {total}")
        self.prg["value"] = pct

    def _do_sort(self):
        if self.var_sort.get() == "id":
            self._workers.sort()
        else:
            self._workers.sort(key=lambda w: w.fio)
        self._refresh()
        self.txt.add("--- Отсортировано ---")

    def _refresh(self):
        self.txt.clear()
        self.txt.add(f"Всего сотрудников: {len(self._workers)}")
        self.txt.add(f"Ролей в хранилище: {len(self._roles)}")
        self.txt.add("--- Список ---")
        for w in self._workers:
            self.txt.add(str(w))
        self.prg["value"] = 100

    # закрытие + сохранение отчёта
    def _quit(self):
        self._t_out = datetime.now()
        line = self.report_line(
            self._login, self._t_in, self._t_out, self._uname
        )
        try:
            d = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(d, "report.txt")
            with open(path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
            print("Отчёт записан:")
            print(line)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось записать отчёт:\n{e}")
        self.root.destroy()


# точка входа
def main():
    root = tk.Tk()
    win = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()