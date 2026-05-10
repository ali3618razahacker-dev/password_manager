import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from database import DatabaseManager
from crypto_utils import CryptoManager
from ui_components import PasswordGenerator, EntryCard

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SecureVaultApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SecureVault - Professional Password Manager")
        self.geometry("900x600")
        
        self.db = DatabaseManager()
        self.crypto = CryptoManager()
        
        self.current_user = None
        self.session_key = None
        
        # UI Setup
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.show_login()

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_screen()
        self.login_frame = ctk.CTkFrame(self, width=400, height=500)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(self.login_frame, text="SecureVault", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(40, 20))
        
        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Username", width=250)
        self.username_entry.pack(pady=10)
        
        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Master Password", show="*", width=250)
        self.password_entry.pack(pady=10)
        
        ctk.CTkButton(self.login_frame, text="Login", width=250, command=self.login).pack(pady=(20, 10))
        ctk.CTkButton(self.login_frame, text="Create Account", width=250, fg_color="transparent", border_width=2, command=self.signup).pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        user = self.db.get_user(username)
        if user and self.crypto.verify_password(password, user[2]):
            self.current_user = user
            self.session_key = self.crypto.derive_key(password, user[3])
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if len(username) < 3 or len(password) < 8:
            messagebox.showwarning("Warning", "Username must be > 3 and Password > 8 chars")
            return
            
        salt = self.crypto.generate_salt()
        hashed = self.crypto.hash_password(password)
        
        if self.db.create_user(username, hashed, salt):
            messagebox.showinfo("Success", "Account created! Please login.")
        else:
            messagebox.showerror("Error", "Username already exists")

    def show_dashboard(self):
        self.clear_screen()
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        ctk.CTkLabel(self.sidebar, text="SecureVault", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=20)
        
        self.cat_all_btn = ctk.CTkButton(self.sidebar, text="All Passwords", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.load_entries("All"))
        self.cat_all_btn.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.cat_social_btn = ctk.CTkButton(self.sidebar, text="Social", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: self.load_entries("Social"))
        self.cat_social_btn.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.gen_pw_btn = ctk.CTkButton(self.sidebar, text="Generator", fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", command=lambda: PasswordGenerator(self))
        self.gen_pw_btn.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.logout_btn = ctk.CTkButton(self.sidebar, text="Logout", fg_color="#E74C3C", hover_color="#C0392B", command=self.show_login)
        self.logout_btn.grid(row=5, column=0, padx=20, pady=20, sticky="ew")
        
        # Main Content
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)
        
        # Header
        self.header = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header.grid_columnconfigure(0, weight=1)
        
        self.search_entry = ctk.CTkEntry(self.header, placeholder_text="Search sites...", width=300)
        self.search_entry.grid(row=0, column=0, sticky="w")
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_entries())
        
        self.add_btn = ctk.CTkButton(self.header, text="+ Add New", width=120, command=self.show_add_entry_dialog)
        self.add_btn.grid(row=0, column=1, sticky="e")
        
        # Entries List
        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_content, label_text="Vault Entries")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew")
        self.scrollable_frame.columnconfigure(0, weight=1)
        
        self.load_entries()

    def load_entries(self, category=None):
        search = self.search_entry.get() if hasattr(self, 'search_entry') else None
        entries = self.db.get_entries(self.current_user[0], category, search)
        
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        for i, entry in enumerate(entries):
            card = EntryCard(self.scrollable_frame, entry, on_view=self.view_entry, on_delete=self.delete_entry)
            card.grid(row=i, column=0, padx=10, pady=5, sticky="ew")

    def show_add_entry_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Entry")
        dialog.geometry("400x500")
        dialog.after(10, dialog.lift)
        
        ctk.CTkLabel(dialog, text="Add Account", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        site_e = ctk.CTkEntry(dialog, placeholder_text="Site/App Name", width=300)
        site_e.pack(pady=10)
        
        user_e = ctk.CTkEntry(dialog, placeholder_text="Username/Email", width=300)
        user_e.pack(pady=10)
        
        pass_e = ctk.CTkEntry(dialog, placeholder_text="Password", show="*", width=300)
        pass_e.pack(pady=10)
        
        url_e = ctk.CTkEntry(dialog, placeholder_text="URL (optional)", width=300)
        url_e.pack(pady=10)
        
        cat_e = ctk.CTkOptionMenu(dialog, values=["General", "Social", "Work", "Finance", "Other"], width=300)
        cat_e.pack(pady=10)
        
        def save():
            encrypted = self.crypto.encrypt(pass_e.get(), self.session_key)
            self.db.add_entry(self.current_user[0], site_e.get(), user_e.get(), encrypted, url_e.get(), cat_e.get())
            dialog.destroy()
            self.load_entries()
            
        ctk.CTkButton(dialog, text="Save Entry", width=300, command=save).pack(pady=20)

    def view_entry(self, entry_data):
        # Decrypt password for viewing
        decrypted = self.crypto.decrypt(entry_data[4], self.session_key)
        
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Details: {entry_data[2]}")
        dialog.geometry("400x300")
        dialog.after(10, dialog.lift)
        
        ctk.CTkLabel(dialog, text=entry_data[2], font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        ctk.CTkLabel(dialog, text=f"Username: {entry_data[3]}").pack(pady=5)
        
        pass_var = ctk.StringVar(value=decrypted)
        e = ctk.CTkEntry(dialog, textvariable=pass_var, width=250)
        e.pack(pady=10)
        
        def copy_pass():
            self.clipboard_clear()
            self.clipboard_append(decrypted)
            messagebox.showinfo("Copied", "Password copied to clipboard!")

        ctk.CTkButton(dialog, text="Copy Password", command=copy_pass).pack(pady=10)

    def delete_entry(self, entry_id):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this entry?"):
            self.db.delete_entry(entry_id)
            self.load_entries()

if __name__ == "__main__":
    app = SecureVaultApp()
    app.mainloop()
