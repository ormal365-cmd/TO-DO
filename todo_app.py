import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import json
import os

class CuteTodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎀 투두리스트")
        self.root.geometry("450x650")
        
        # 색상 테마 설정
        self.bg_color = "#FFF0F5"
        self.todo_color = "#FFB6C1"
        self.acc_color = "#D8BFD8"
        self.text_color = "#555555"
        
        self.root.configure(bg=self.bg_color)
        
        self.tasks = []
        self.accounts = []
        
        self.font_main = ("Malgun Gothic", 11)
        
        # 탭 스타일(ttk) 설정
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=self.bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', font=("Malgun Gothic", 11, "bold"), padding=[20, 5], background="#FFE4E1", foreground="#888888")
        style.map('TNotebook.Tab', 
                  background=[('selected', '#FF69B4')], 
                  foreground=[('selected', 'white')])
        
        style.configure("Treeview", font=("Malgun Gothic", 10), rowheight=30, borderwidth=0)
        style.configure("Treeview.Heading", font=("Malgun Gothic", 10, "bold"), background="#FFE4E1", foreground=self.text_color)
        style.map('Treeview', background=[('selected', '#FFC0CB')])

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)

        # 탭 프레임 생성
        self.tab_todo = tk.Frame(self.notebook, bg="white", padx=15, pady=15)
        self.tab_account = tk.Frame(self.notebook, bg="white", padx=15, pady=15)

        self.notebook.add(self.tab_todo, text="🐰 할 일")
        self.notebook.add(self.tab_account, text="🔐 비밀 수첩")

        self.data_file = "cute_todo_data.json"
        self.load_data()

        self.setup_todo_tab()
        self.setup_account_tab()
        
        self.update_task_listbox()
        self.update_account_tree()
        
        self.check_alarms()

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.accounts = data.get("accounts", [])
                    
                    raw_tasks = data.get("tasks", [])
                    today = datetime.datetime.now().date()
                    self.tasks = []
                    
                    for t in raw_tasks:
                        try:
                            due_time = datetime.datetime.strptime(t["due"], "%Y-%m-%d %H:%M")
                            task_id = t.get("id", due_time.timestamp()) 
                            task_date = datetime.datetime.fromtimestamp(task_id).date()
                            
                            # '오늘' 데이터만 유지 (어제 데이터는 자동 폐기)
                            if task_date == today:
                                self.tasks.append({
                                    "task": t["task"],
                                    "due": due_time,
                                    "completed": t.get("completed", False),
                                    "notified": t.get("notified", False),
                                    "id": task_id
                                })
                        except ValueError:
                            pass
            except Exception as e:
                print(f"데이터 로드 중 에러 발생: {e}")

    def save_data(self):
        data = {
            "tasks": [{
                "task": t["task"], 
                "due": t["due"].strftime("%Y-%m-%d %H:%M"), 
                "completed": t["completed"], 
                "notified": t["notified"],
                "id": t["id"]
            } for t in self.tasks],
            "accounts": self.accounts
        }
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"데이터 저장 중 에러 발생: {e}")

    def setup_todo_tab(self):
        tk.Label(self.tab_todo, text="✨ 무엇을 할까요?", font=self.font_main, bg="white", fg=self.text_color).pack(anchor="w")
        self.task_entry = tk.Entry(self.tab_todo, font=self.font_main, relief="solid", bd=1)
        self.task_entry.pack(fill="x", pady=(5, 15), ipady=5)
        
        tk.Label(self.tab_todo, text="⏰ 언제 알려줄까요?", font=self.font_main, bg="white", fg=self.text_color).pack(anchor="w")
        self.time_entry = tk.Entry(self.tab_todo, font=self.font_main, relief="solid", bd=1)
        self.time_entry.pack(fill="x", pady=(5, 5), ipady=5)
        
        now = datetime.datetime.now() + datetime.timedelta(minutes=1)
        self.time_entry.insert(0, now.strftime("%Y-%m-%d %H:%M"))
        tk.Label(self.tab_todo, text="(형식: 2026-07-03 12:30)", font=("Malgun Gothic", 9), bg="white", fg="#AAAAAA").pack(anchor="e")
        
        add_btn = tk.Button(self.tab_todo, text="💖 추가하기 💖", bg=self.todo_color, fg="white", font=("Malgun Gothic", 11, "bold"), 
                            relief="flat", cursor="hand2", command=self.add_task)
        add_btn.pack(fill="x", pady=10, ipady=5)
        
        tk.Label(self.tab_todo, text="🌟 기다리는 중인 할 일", font=self.font_main, bg="white", fg=self.text_color).pack(anchor="w", pady=(10,0))
        self.task_listbox = tk.Listbox(self.tab_todo, font=self.font_main, height=8, bg="#FFF0F5", fg=self.text_color, relief="flat")
        self.task_listbox.pack(fill="both", expand=True, pady=5)
        
        btn_todo_frame = tk.Frame(self.tab_todo, bg="white")
        btn_todo_frame.pack(fill="x", pady=5)

        comp_btn = tk.Button(btn_todo_frame, text="✓ 완료 토글", bg="white", fg="#32CD32", font=("Malgun Gothic", 9, "bold"), 
                            relief="solid", bd=1, cursor="hand2", command=self.toggle_task)
        comp_btn.pack(side="left", fill="x", expand=True, padx=(0, 2))

        del_btn = tk.Button(btn_todo_frame, text="✖ 선택 지우기", bg="white", fg="#FF69B4", font=("Malgun Gothic", 9, "bold"), 
                            relief="solid", bd=1, cursor="hand2", command=self.delete_task)
        del_btn.pack(side="left", fill="x", expand=True, padx=(2, 0))

    def setup_account_tab(self):
        tk.Label(self.tab_account, text="🌐 사이트 이름", font=self.font_main, bg="white", fg=self.text_color).pack(anchor="w")
        self.site_entry = tk.Entry(self.tab_account, font=self.font_main, relief="solid", bd=1)
        self.site_entry.pack(fill="x", pady=(2, 10), ipady=3)

        tk.Label(self.tab_account, text="👤 아이디", font=self.font_main, bg="white", fg=self.text_color).pack(anchor="w")
        self.id_entry = tk.Entry(self.tab_account, font=self.font_main, relief="solid", bd=1)
        self.id_entry.pack(fill="x", pady=(2, 10), ipady=3)

        tk.Label(self.tab_account, text="🔑 비밀번호", font=self.font_main, bg="white", fg=self.text_color).pack(anchor="w")
        self.pw_entry = tk.Entry(self.tab_account, font=self.font_main, show="*", relief="solid", bd=1)
        self.pw_entry.pack(fill="x", pady=(2, 10), ipady=3)

        add_btn = tk.Button(self.tab_account, text="🔒 비밀 저장하기 🔒", bg=self.acc_color, fg="white", font=("Malgun Gothic", 11, "bold"), 
                            relief="flat", cursor="hand2", command=self.add_account)
        add_btn.pack(fill="x", pady=5, ipady=5)

        header_frame = tk.Frame(self.tab_account, bg="white")
        header_frame.pack(fill="x", pady=(10, 0))
        tk.Label(header_frame, text="📚 나의 비밀 수첩", font=self.font_main, bg="white", fg=self.text_color).pack(side="left")
        
        self.search_entry = tk.Entry(header_frame, font=("Malgun Gothic", 10), relief="solid", bd=1, width=12)
        self.search_entry.pack(side="right", ipady=2)
        self.search_entry.insert(0, "🔍 검색")
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.delete(0, tk.END) if self.search_entry.get() == "🔍 검색" else None)
        self.search_entry.bind("<FocusOut>", lambda e: self.search_entry.insert(0, "🔍 검색") if not self.search_entry.get() else None)
        self.search_entry.bind("<KeyRelease>", self.update_account_tree)
        
        columns = ("site", "id", "pw")
        self.acc_tree = ttk.Treeview(self.tab_account, columns=columns, show="headings", height=5)
        self.acc_tree.heading("site", text="사이트")
        self.acc_tree.heading("id", text="아이디")
        self.acc_tree.heading("pw", text="비밀번호")
        
        self.acc_tree.column("site", width=100)
        self.acc_tree.column("id", width=120)
        self.acc_tree.column("pw", width=100)
        self.acc_tree.pack(fill="both", expand=True, pady=5)

        btn_frame = tk.Frame(self.tab_account, bg="white")
        btn_frame.pack(fill="x")
        
        del_btn = tk.Button(btn_frame, text="✖ 삭제", bg="white", fg="#9370DB", font=("Malgun Gothic", 9, "bold"), 
                            relief="solid", bd=1, cursor="hand2", command=self.delete_account)
        del_btn.pack(side="left", fill="x", expand=True, padx=(0, 2))

        view_btn = tk.Button(btn_frame, text="👀 PW확인", bg="white", fg="#9370DB", font=("Malgun Gothic", 9, "bold"), 
                             relief="solid", bd=1, cursor="hand2", command=self.toggle_password)
        view_btn.pack(side="left", fill="x", expand=True, padx=(2, 2))

        copy_id_btn = tk.Button(btn_frame, text="📋 ID복사", bg="white", fg="#4682B4", font=("Malgun Gothic", 9, "bold"), 
                             relief="solid", bd=1, cursor="hand2", command=self.copy_id)
        copy_id_btn.pack(side="left", fill="x", expand=True, padx=(2, 2))

        copy_pw_btn = tk.Button(btn_frame, text="📋 PW복사", bg="white", fg="#4682B4", font=("Malgun Gothic", 9, "bold"), 
                             relief="solid", bd=1, cursor="hand2", command=self.copy_pw)
        copy_pw_btn.pack(side="left", fill="x", expand=True, padx=(2, 0))

    def add_task(self):
        task_text = self.task_entry.get().strip()
        time_str = self.time_entry.get().strip()
        if not task_text:
            messagebox.showwarning("앗!", "할 일을 입력해야 해요! 🥺")
            return
        try:
            due_time = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("에러!", "올바른 시간 형식이 아니에요! 💦")
            return
        if due_time <= datetime.datetime.now():
            messagebox.showwarning("시간 이상!", "지금보다 나중 시간으로 설정해 주세요! 🕰️")
            return
            
        self.tasks.append({"task": task_text, "due": due_time, "completed": False, "notified": False, "id": datetime.datetime.now().timestamp()})
        self.save_data()
        self.update_task_listbox()
        self.task_entry.delete(0, tk.END)
        messagebox.showinfo("성공!", f"'{task_text}' (이)가 저장되었어요! ✨")

    def delete_task(self):
        sel = self.task_listbox.curselection()
        if not sel: return
        for index in reversed(sel):
            del self.tasks[index]
        self.save_data()
        self.update_task_listbox()

    def toggle_task(self):
        sel = self.task_listbox.curselection()
        if not sel: return
        for index in sel:
            self.tasks[index]["completed"] = not self.tasks[index]["completed"]
        self.save_data()
        self.update_task_listbox()

    def update_task_listbox(self):
        self.task_listbox.delete(0, tk.END)
        for i, t in enumerate(self.tasks):
            time_formatted = t["due"].strftime("%y/%m/%d %H:%M")
            status = "♥" if t.get("completed") else " "
            self.task_listbox.insert(tk.END, f"[{status}] [{time_formatted}] 🌱 {t['task']}")
            if t.get("completed"):
                self.task_listbox.itemconfig(i, {'fg': '#AAAAAA'})

    def add_account(self):
        site = self.site_entry.get().strip()
        uid = self.id_entry.get().strip()
        pw = self.pw_entry.get().strip()
        
        if not site or not uid or not pw:
            messagebox.showwarning("앗!", "모든 칸을 채워주세요! 📝")
            return
            
        self.accounts.append({"site": site, "id": uid, "pw": pw, "show": False})
        self.save_data()
        self.update_account_tree()
        
        self.site_entry.delete(0, tk.END)
        self.id_entry.delete(0, tk.END)
        self.pw_entry.delete(0, tk.END)
        messagebox.showinfo("저장 완료", "비밀 수첩에 저장했어요! 🔒")

    def delete_account(self):
        sel = self.acc_tree.selection()
        if not sel: return
        for item in reversed(sel):
            values = self.acc_tree.item(item, 'values')
            for i, acc in enumerate(self.accounts):
                if acc["site"] == values[0] and acc["id"] == values[1]:
                    del self.accounts[i]
                    break
        self.save_data()
        self.update_account_tree()

    def toggle_password(self):
        sel = self.acc_tree.selection()
        if not sel: return
        item = sel[0]
        values = self.acc_tree.item(item, 'values')
        
        for acc in self.accounts:
            if acc["site"] == values[0] and acc["id"] == values[1]:
                acc["show"] = not acc["show"]
                break
                
        self.update_account_tree()

    def update_account_tree(self, event=None):
        for item in self.acc_tree.get_children():
            self.acc_tree.delete(item)
            
        search_query = self.search_entry.get().strip().lower()
        if search_query == "🔍 검색":
            search_query = ""
            
        for acc in self.accounts:
            if search_query in acc["site"].lower():
                pw_display = acc["pw"] if acc["show"] else "********"
                self.acc_tree.insert("", "end", values=(acc["site"], acc["id"], pw_display))

    def copy_id(self):
        sel = self.acc_tree.selection()
        if not sel: return
        item = sel[0]
        values = self.acc_tree.item(item, 'values')
        uid = values[1]
        self.root.clipboard_clear()
        self.root.clipboard_append(uid)
        messagebox.showinfo("복사 완료", "아이디가 클립보드에 복사되었습니다! 📋")

    def copy_pw(self):
        sel = self.acc_tree.selection()
        if not sel: return
        item = sel[0]
        values = self.acc_tree.item(item, 'values')
        site_name = values[0]
        uid = values[1]
        for acc in self.accounts:
            if acc["site"] == site_name and acc["id"] == uid:
                self.root.clipboard_clear()
                self.root.clipboard_append(acc["pw"])
                messagebox.showinfo("복사 완료", "비밀번호가 클립보드에 복사되었습니다! 📋")
                break

    def check_alarms(self):
        now = datetime.datetime.now()
        needs_update = False
        for t in self.tasks:
            if not t.get("completed") and not t.get("notified") and now >= t["due"]:
                messagebox.showinfo("알림 ⏰", f"{t['task']}\n\n다 하셨나요? 🚀")
                t["notified"] = True
                needs_update = True
        
        if needs_update:
            self.save_data()
            self.update_task_listbox()
        self.root.after(1000, self.check_alarms)

if __name__ == "__main__":
    root = tk.Tk()
    app = CuteTodoApp(root)
    root.mainloop()
