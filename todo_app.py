
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
