import customtkinter as ctk
import string
import random

class PasswordGenerator(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Password Generator")
        self.geometry("400x350")
        self.resizable(False, False)
        self.after(10, self.lift) # Ensure it stays on top
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame = ctk.CTkFrame(self)
        self.frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.frame.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self.frame, text="Secure Password Generator", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.grid(row=0, column=0, pady=(0, 20))

        # Result Entry
        self.result_var = ctk.StringVar(value="")
        self.result_entry = ctk.CTkEntry(self.frame, textvariable=self.result_var, font=ctk.CTkFont(size=16))
        self.result_entry.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Length Slider
        self.length_label = ctk.CTkLabel(self.frame, text="Length: 16")
        self.length_label.grid(row=2, column=0, pady=(0, 5))
        
        self.length_slider = ctk.CTkSlider(self.frame, from_=8, to=32, number_of_steps=24, command=self.update_length_label)
        self.length_slider.set(16)
        self.length_slider.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Checkboxes
        self.check_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.check_frame.grid(row=4, column=0, pady=(0, 20))
        
        self.symbols_var = ctk.BooleanVar(value=True)
        self.symbols_check = ctk.CTkCheckBox(self.check_frame, text="Symbols", variable=self.symbols_var)
        self.symbols_check.pack(side="left", padx=10)
        
        self.numbers_var = ctk.BooleanVar(value=True)
        self.numbers_check = ctk.CTkCheckBox(self.check_frame, text="Numbers", variable=self.numbers_var)
        self.numbers_check.pack(side="left", padx=10)

        # Buttons
        self.gen_button = ctk.CTkButton(self.frame, text="Generate", command=self.generate)
        self.gen_button.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        self.copy_button = ctk.CTkButton(self.frame, text="Copy to Clipboard", fg_color="gray", command=self.copy)
        self.copy_button.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.generate()

    def update_length_label(self, value):
        self.length_label.configure(text=f"Length: {int(value)}")

    def generate(self):
        length = int(self.length_slider.get())
        chars = string.ascii_letters
        if self.numbers_var.get():
            chars += string.digits
        if self.symbols_var.get():
            chars += string.punctuation
            
        password = "".join(random.choice(chars) for _ in range(length))
        self.result_var.set(password)

    def copy(self):
        self.clipboard_clear()
        self.clipboard_append(self.result_var.get())

class EntryCard(ctk.CTkFrame):
    def __init__(self, master, entry_data, on_view, on_delete, **kwargs):
        super().__init__(master, **kwargs)
        self.entry_data = entry_data # (id, user_id, site_name, username, encrypted, url, category, ...)
        
        self.grid_columnconfigure(0, weight=1)
        
        self.site_label = ctk.CTkLabel(self, text=entry_data[2], font=ctk.CTkFont(size=14, weight="bold"))
        self.site_label.grid(row=0, column=0, padx=15, pady=(10, 0), sticky="w")
        
        self.user_label = ctk.CTkLabel(self, text=entry_data[3], font=ctk.CTkFont(size=12), text_color="gray")
        self.user_label.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="w")
        
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=0, column=1, rowspan=2, padx=10)
        
        self.view_btn = ctk.CTkButton(self.btn_frame, text="View", width=60, height=25, command=lambda: on_view(entry_data))
        self.view_btn.pack(side="left", padx=5)
        
        self.del_btn = ctk.CTkButton(self.btn_frame, text="Del", width=60, height=25, fg_color="#E74C3C", hover_color="#C0392B", command=lambda: on_delete(entry_data[0]))
        self.del_btn.pack(side="left", padx=5)
