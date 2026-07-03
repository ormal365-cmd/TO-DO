import customtkinter as ctk
from tkinter import messagebox
import datetime
import json
import os

# 🎀 둥글둥글 귀여운 모던 테마 설정 🎀
ctk.set_appearance_mode("light")

class CuteTodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🎀 큐트 투두 & 비밀수첩")
        self.geometry("450x720")
        self.configure(fg_color="#FFF0F5") # 전체 딸기우유빛 배경
        
        self.tasks = []
        self.accounts = []
        self.data_file = "cute_todo_data.json"
        
        # 폰트 설정
        self.font_main = ("Malgun Gothic", 13)
        self.font_bold = ("Malgun Gothic", 14, "bold")
        
        # 푹신푹신한 탭 뷰 생성 (둥근 모서리!)
        self.tabview = ctk.CTkTabview(self, 
                                      fg_color="#FFE4E1",
                                      segmented_button_fg_color="#FFC0CB",
                                      segmented_button_selected_color="#FF69B4",
                                      segmented_button_selected_hover_color="#FF1493",
                                      segmented_button_unselected_color="#FFC0CB",
                                      segmented_button_unselected_hover_color="#FFB6C1",
                                      text_color="white", corner_radius=15)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        self.tab_todo = self.tabview.add("🐰 할 일")
        self.tab_account = self.tabview.add("🔐 비밀 수첩")

        self.load_data()
        self.setup_todo_tab()
        self.setup_account_tab()
        
        self.update_task_list()
        self.update_account_list()
        
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
                print(f"데이터 불러오기 에러: {e}")

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
            print(f"데이터 저장 에러: {e}")

    def setup_todo_tab(self):
        # 둥근 텍스트 입력창
        ctk.CTkLabel(self.tab_todo, text="✨ 무엇을 할까요?", font=self.font_bold, text_color="#FF69B4").pack(anchor="w", pady=(10, 2))
        self.task_entry = ctk.CTkEntry(self.tab_todo, font=self.font_main, fg_color="white", border_color="#FFB6C1", text_color="#555555", corner_radius=10, height=38)
        self.task_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(self.tab_todo, text="⏰ 언제 알려줄까요?", font=self.font_bold, text_color="#FF69B4").pack(anchor="w", pady=(5, 2))
        self.time_entry = ctk.CTkEntry(self.tab_todo, font=self.font_main, fg_color="white", border_color="#FFB6C1", text_color="#555555", corner_radius=10, height=38)
        self.time_entry.pack(fill="x", pady=(0, 2))
        
        now = datetime.datetime.now() + datetime.timedelta(minutes=1)
        self.time_entry.insert(0, now.strftime("%Y-%m-%d %H:%M"))
        ctk.CTkLabel(self.tab_todo, text="(형식: 2026-07-03 12:30)", font=("Malgun Gothic", 11), text_color="#AAAAAA").pack(anchor="e")
        
        add_btn = ctk.CTkButton(self.tab_todo, text="💖 추가하기 💖", font=self.font_bold, fg_color="#FFB6C1", hover_color="#FF69B4", text_color="white", corner_radius=20, height=45, command=self.add_task)
        add_btn.pack(fill="x", pady=10)
        
        ctk.CTkLabel(self.tab_todo, text="🌟 기다리는 중인 할 일", font=self.font_bold, text_color="#FF69B4").pack(anchor="w", pady=(10,5))
        
        # 예쁜 스크롤 리스트 (웹 버전 느낌!)
        self.task_scroll = ctk.CTkScrollableFrame(self.tab_todo, fg_color="white", border_color="#FFC0CB", border_width=2, corner_radius=10)
        self.task_scroll.pack(fill="both", expand=True, pady=5)

    def setup_account_tab(self):
        input_frame = ctk.CTkFrame(self.tab_account, fg_color="transparent")
        input_frame.pack(fill="x", pady=5)

        self.site_entry = ctk.CTkEntry(input_frame, placeholder_text="🌐 사이트 이름", font=self.font_main, fg_color="white", border_color="#D8BFD8", text_color="#555", corner_radius=10, height=38)
        self.site_entry.pack(fill="x", pady=4)

        self.id_entry = ctk.CTkEntry(input_frame, placeholder_text="👤 아이디", font=self.font_main, fg_color="white", border_color="#D8BFD8", text_color="#555", corner_radius=10, height=38)
        self.id_entry.pack(fill="x", pady=4)

        self.pw_entry = ctk.CTkEntry(input_frame, placeholder_text="🔑 비밀번호", show="*", font=self.font_main, fg_color="white", border_color="#D8BFD8", text_color="#555", corner_radius=10, height=38)
        self.pw_entry.pack(fill="x", pady=4)

        add_btn = ctk.CTkButton(self.tab_account, text="🔒 비밀 저장하기 🔒", font=self.font_bold, fg_color="#D8BFD8", hover_color="#BA55D3", text_color="white", corner_radius=20, height=45, command=self.add_account)
        add_btn.pack(fill="x", pady=10)

        search_frame = ctk.CTkFrame(self.tab_account, fg_color="transparent")
        search_frame.pack(fill="x", pady=(10, 5))

        ctk.CTkLabel(search_frame, text="📚 나의 비밀 수첩", font=self.font_bold, text_color="#BA55D3").pack(side="left")

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="🔍 검색", width=120, height=32, font=self.font_main, fg_color="white", border_color="#D8BFD8", text_color="#555", corner_radius=15)
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", self.update_account_list)

        self.acc_scroll = ctk.CTkScrollableFrame(self.tab_account, fg_color="white", border_color="#E6E6FA", border_width=2, corner_radius=10)
        self.acc_scroll.pack(fill="both", expand=True, pady=5)

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
        self.update_task_list()
        self.task_entry.delete(0, 'end')

    def toggle_task(self, task):
        task["completed"] = not task.get("completed", False)
        self.save_data()
        self.update_task_list()

    def delete_task(self, task):
        self.tasks.remove(task)
        self.save_data()
        self.update_task_list()

    def update_task_list(self):
        for widget in self.task_scroll.winfo_children():
            widget.destroy()
            
        for t in self.tasks:
            frame = ctk.CTkFrame(self.task_scroll, fg_color="#FFF0F5", corner_radius=10)
            frame.pack(fill="x", pady=4, padx=4)
            
            time_formatted = t["due"].strftime("%y/%m/%d %H:%M")
            is_completed = t.get("completed", False)
            
            cb = ctk.CTkCheckBox(frame, text=f"[{time_formatted}] {t['task']}", 
                                 command=lambda task=t: self.toggle_task(task),
                                 font=self.font_main, 
                                 text_color="#AAAAAA" if is_completed else "#555555",
                                 fg_color="#FF69B4", hover_color="#FF1493", border_color="#FFB6C1",
                                 corner_radius=5)
            if is_completed:
                cb.select()
            else:
                cb.deselect()
                
            cb.pack(side="left", padx=10, pady=12, fill="x", expand=True)
            
            del_btn = ctk.CTkButton(frame, text="✖", width=30, height=30, fg_color="transparent", hover_color="#FFE4E1", text_color="#FF69B4", font=self.font_bold, command=lambda task=t: self.delete_task(task))
            del_btn.pack(side="right", padx=5)

    def add_account(self):
        site = self.site_entry.get().strip()
        uid = self.id_entry.get().strip()
        pw = self.pw_entry.get().strip()
        
        if not site or not uid or not pw:
            messagebox.showwarning("앗!", "모든 칸을 채워주세요! 📝")
            return
            
        self.accounts.append({"site": site, "id": uid, "pw": pw, "show": False})
        self.save_data()
        self.update_account_list()
        
        self.site_entry.delete(0, 'end')
        self.id_entry.delete(0, 'end')
        self.pw_entry.delete(0, 'end')

    def delete_account(self, acc):
        self.accounts.remove(acc)
        self.save_data()
        self.update_account_list()

    def toggle_password(self, acc):
        acc["show"] = not acc.get("show", False)
        self.update_account_list()

    def update_account_list(self, event=None):
        for widget in self.acc_scroll.winfo_children():
            widget.destroy()
            
        search_query = self.search_entry.get().strip().lower()
        if search_query == "🔍 검색":
            search_query = ""
            
        for acc in self.accounts:
            if search_query in acc["site"].lower():
                frame = ctk.CTkFrame(self.acc_scroll, fg_color="#F8F8FF", corner_radius=10, border_color="#E6E6FA", border_width=1)
                frame.pack(fill="x", pady=5, padx=5)
                
                info_frame = ctk.CTkFrame(frame, fg_color="transparent")
                info_frame.pack(fill="x", padx=10, pady=(10, 5))
                
                site_label = ctk.CTkLabel(info_frame, text=acc["site"], font=self.font_bold, text_color="#8A2BE2")
                site_label.pack(side="left")
                
                pw_display = acc["pw"] if acc.get("show") else "********"
                id_pw_label = ctk.CTkLabel(info_frame, text=f"ID: {acc['id']}  |  PW: {pw_display}", font=self.font_main, text_color="#777")
                id_pw_label.pack(side="right")
                
                btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
                btn_frame.pack(fill="x", padx=10, pady=(0,10))
                
                del_btn = ctk.CTkButton(btn_frame, text="✖ 삭제", width=50, height=26, fg_color="#FFB6C1", hover_color="#FF69B4", text_color="white", font=("Malgun Gothic", 11, "bold"), corner_radius=8, command=lambda a=acc: self.delete_account(a))
                del_btn.pack(side="left", padx=(0,5))
                
                view_btn = ctk.CTkButton(btn_frame, text="👀 PW확인", width=60, height=26, fg_color="#D8BFD8", hover_color="#BA55D3", text_color="white", font=("Malgun Gothic", 11, "bold"), corner_radius=8, command=lambda a=acc: self.toggle_password(a))
                view_btn.pack(side="left", padx=5)
                
                copy_id_btn = ctk.CTkButton(btn_frame, text="📋 ID복사", width=60, height=26, fg_color="#B0C4DE", hover_color="#4682B4", text_color="white", font=("Malgun Gothic", 11, "bold"), corner_radius=8, command=lambda a=acc: self.copy_id(a))
                copy_id_btn.pack(side="right", padx=(5,0))
                
                copy_pw_btn = ctk.CTkButton(btn_frame, text="📋 PW복사", width=60, height=26, fg_color="#B0C4DE", hover_color="#4682B4", text_color="white", font=("Malgun Gothic", 11, "bold"), corner_radius=8, command=lambda a=acc: self.copy_pw(a))
                copy_pw_btn.pack(side="right", padx=5)

    def copy_id(self, acc):
        self.clipboard_clear()
        self.clipboard_append(acc["id"])
        messagebox.showinfo("복사 완료", "아이디가 클립보드에 복사되었습니다! 📋")

    def copy_pw(self, acc):
        self.clipboard_clear()
        self.clipboard_append(acc["pw"])
        messagebox.showinfo("복사 완료", "비밀번호가 클립보드에 복사되었습니다! 📋")

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
            self.update_task_list()
        self.after(1000, self.check_alarms)

if __name__ == "__main__":
    app = CuteTodoApp()
    app.mainloop()
