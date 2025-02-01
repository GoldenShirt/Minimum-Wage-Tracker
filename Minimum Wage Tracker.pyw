import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import json
import os

class WorkHoursApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minimum Wage Tracker")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.data = []
        self.wage_per_hour = 32  # Default wage
        self.language = "English"  # Default language
        self.load_data()
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.save_data_and_exit)

    def create_widgets(self):
        # Main container frame with three columns: left spacer, center inputs, right spacer.
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)  # Center column for inputs
        main_frame.columnconfigure(2, weight=1)

        current_row = 0

        # ---- Language Selection Frame ----
        lang_frame = ttk.Frame(main_frame)
        lang_frame.grid(row=current_row, column=1, sticky="ew", pady=5)
        self.language_var = tk.StringVar(value=self.language)
        # For Hebrew (RTL), place label on the right and combobox on the left.
        if self.language == "עברית":
            ttk.Label(lang_frame, text=self.translate(":Language / שפה")).grid(row=0, column=1, sticky="e")
            language_menu = ttk.Combobox(lang_frame, textvariable=self.language_var, state="readonly", width=10)
            language_menu.grid(row=0, column=0, padx=5, sticky="w")
        else:
            ttk.Label(lang_frame, text=self.translate(":Language / שפה")).grid(row=0, column=0, sticky="w")
            language_menu = ttk.Combobox(lang_frame, textvariable=self.language_var, state="readonly", width=10)
            language_menu.grid(row=0, column=1, padx=5, sticky="w")
        language_menu['values'] = ("English", "עברית")
        language_menu.bind("<<ComboboxSelected>>", self.switch_language)
        current_row += 1

        # ---- Wage Input Frame ----
        wage_frame = ttk.Frame(main_frame)
        wage_frame.grid(row=current_row, column=1, sticky="ew", pady=5)
        if self.language == "עברית":
            self.wage_label = ttk.Label(wage_frame, text=self.translate("Wage per hour (NIS):"))
            self.wage_label.grid(row=0, column=1, sticky="e")
            self.wage_entry = ttk.Entry(wage_frame, justify="right", width=10)
            self.wage_entry.grid(row=0, column=0, padx=5, sticky="w")
        else:
            self.wage_label = ttk.Label(wage_frame, text=self.translate("Wage per hour (NIS):"))
            self.wage_label.grid(row=0, column=0, sticky="w")
            self.wage_entry = ttk.Entry(wage_frame, justify="left", width=10)
            self.wage_entry.grid(row=0, column=1, padx=5, sticky="w")
        self.wage_entry.insert(0, str(int(self.wage_per_hour)))
        self.wage_entry.bind("<FocusOut>", self.update_wage)
        self.wage_entry.bind("<Return>", self.update_wage)
        current_row += 1

        # ---- New Entry Input Fields Frame ----
        input_frame = ttk.LabelFrame(main_frame, text=self.translate("New Entry"), padding=10)
        input_frame.grid(row=current_row, column=1, sticky="ew", pady=10)
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=1)

        # For each row, swap the order if Hebrew (RTL)
        if self.language == "עברית":
            # Date
            ttk.Label(input_frame, text=self.translate("Date:")).grid(row=0, column=1, sticky="e", padx=5, pady=2)
            self.date_entry = DateEntry(input_frame, width=12, background='darkblue',
                                        foreground='white', borderwidth=2,
                                        date_pattern='dd/mm/yyyy', justify="right")
            self.date_entry.grid(row=0, column=0, sticky="w", padx=5, pady=2)
            # Start Time
            ttk.Label(input_frame, text=self.translate("Start Time:")).grid(row=1, column=1, sticky="e", padx=5, pady=2)
            self.start_time_entry = ttk.Entry(input_frame, justify="right")
            self.start_time_entry.grid(row=1, column=0, sticky="w", padx=5, pady=2)
            # End Time
            ttk.Label(input_frame, text=self.translate("End Time:")).grid(row=2, column=1, sticky="e", padx=5, pady=2)
            self.end_time_entry = ttk.Entry(input_frame, justify="right")
            self.end_time_entry.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        else:
            # Date
            ttk.Label(input_frame, text=self.translate("Date:")).grid(row=0, column=0, sticky="e", padx=5, pady=2)
            self.date_entry = DateEntry(input_frame, width=12, background='darkblue',
                                        foreground='white', borderwidth=2,
                                        date_pattern='dd/mm/yyyy', justify="left")
            self.date_entry.grid(row=0, column=1, sticky="w", padx=5, pady=2)
            # Start Time
            ttk.Label(input_frame, text=self.translate("Start Time:")).grid(row=1, column=0, sticky="e", padx=5, pady=2)
            self.start_time_entry = ttk.Entry(input_frame, justify="left")
            self.start_time_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
            # End Time
            ttk.Label(input_frame, text=self.translate("End Time:")).grid(row=2, column=0, sticky="e", padx=5, pady=2)
            self.end_time_entry = ttk.Entry(input_frame, justify="left")
            self.end_time_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        current_row += 1

        # ---- Buttons Frame ----
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=current_row, column=1, sticky="ew", pady=5)
        if self.language == "עברית":
            ttk.Button(button_frame, text=self.translate("Add Entry"), command=self.add_entry).pack(side=tk.RIGHT, padx=5)
            ttk.Button(button_frame, text=self.translate("Delete Entry"), command=self.delete_entry).pack(side=tk.RIGHT, padx=5)
        else:
            ttk.Button(button_frame, text=self.translate("Add Entry"), command=self.add_entry).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text=self.translate("Delete Entry"), command=self.delete_entry).pack(side=tk.LEFT, padx=5)
        current_row += 1

        # ---- Table (Existing Entries) ----
        self.table = ttk.Treeview(main_frame, columns=("date", "day", "start", "end", "hours", "earnings"),
                                  show='headings')
        headers = {
            "date": self.translate("Date"),
            "day": self.translate("Day"),
            "start": self.translate("Start Time"),
            "end": self.translate("End Time"),
            "hours": self.translate("Hours Worked"),
            "earnings": self.translate("Earnings (NIS)*")
        }
        for col in self.table["columns"]:
            self.table.heading(col, text=headers[col])
            anchor = "e" if self.language == "עברית" else "w"
            self.table.column(col, width=100, anchor=anchor)
        # The table spans all three columns so its width is unaffected.
        self.table.grid(row=current_row, column=0, columnspan=3, sticky="nsew", pady=5)
        main_frame.rowconfigure(current_row, weight=1)
        self.table.bind("<Double-1>", self.start_edit)
        current_row += 1

        # ---- Totals Frame ----
        totals_frame = ttk.Frame(main_frame)
        totals_frame.grid(row=current_row, column=1, sticky="ew", pady=5)
        if self.language == "עברית":
            self.total_hours_label = ttk.Label(totals_frame, text="", anchor="e")
            self.total_hours_label.grid(row=0, column=1, sticky="e", padx=5)
            self.total_earnings_label = ttk.Label(totals_frame, text="", anchor="e")
            self.total_earnings_label.grid(row=0, column=0, sticky="w", padx=5)
        else:
            self.total_hours_label = ttk.Label(totals_frame, text="", anchor="w")
            self.total_hours_label.grid(row=0, column=0, sticky="w", padx=5)
            self.total_earnings_label = ttk.Label(totals_frame, text="", anchor="w")
            self.total_earnings_label.grid(row=0, column=1, sticky="w", padx=5)
        current_row += 1

        # ---- Note and Import Button Frame ----
        note_frame = ttk.Frame(main_frame)
        note_frame.grid(row=current_row, column=1, sticky="ew", pady=5)
        if self.language == "עברית":
            ttk.Label(note_frame, text=self.translate("* Earnings are estimations"),
                      foreground="gray").grid(row=0, column=1, sticky="e", padx=5)
            ttk.Button(note_frame, text=self.translate("Import Data"),
                       command=self.import_data).grid(row=0, column=0, sticky="w", padx=5)
        else:
            ttk.Label(note_frame, text=self.translate("* Earnings are estimations"),
                      foreground="gray").grid(row=0, column=0, sticky="w", padx=5)
            ttk.Button(note_frame, text=self.translate("Import Data"),
                       command=self.import_data).grid(row=0, column=1, sticky="e", padx=5)

        self.update_table()
        self.update_totals()

    def translate(self, text):
        translations = {
            "Wage per hour (NIS):": "(₪) :שכר לשעה",
            "Date:": ":תאריך",
            "Start Time:": ":שעת התחלה",
            "End Time:": ":שעת סיום",
            "Add Entry": "הוסף רשומה",
            "Delete Entry": "מחק רשומה",
            "Date": "תאריך",
            "Day": "יום",
            "Hours Worked": "שעות עבודה",
            "Earnings (NIS)*": "שכר (₪)*",
            "Import Data": "ייבוא נתונים",
            "* Earnings are estimations": "* השכר הוא הערכה",
            "New Entry": "רשומה חדשה",
            # Totals
            "Total hours worked: ": "סה\"כ שעות עבודה: ",
            "Total earnings: ": "סה\"כ שכר: ",
            " NIS*": " ₪*",
            # Days of the week
            "Sunday": "יום ראשון",
            "Monday": "יום שני",
            "Tuesday": "יום שלישי",
            "Wednesday": "יום רביעי",
            "Thursday": "יום חמישי",
            "Friday": "יום שישי",
            "Saturday": "יום שבת",
            # Error messages
            "Invalid Wage": "שכר לא תקין",
            "Please enter a valid positive number for the wage.": "אנא הכנס מספר חיובי תקין עבור השכר.",
            "Invalid time": "שעה לא תקינה",
            "Please enter time in HH:MM format": "אנא הכנס שעה בפורמט HH:MM",
            "Invalid date": "תאריך לא תקין",
            "Please enter a valid date": "אנא הכנס תאריך תקין",
            "No Selection": "לא נבחרה רשומה",
            "Please select an entry to delete.": "אנא בחר רשומה למחיקה.",
            "Error": "שגיאה",
            "Failed to load data": "טעינת הנתונים נכשלה",
            "Failed to save data": "שמירת הנתונים נכשלה",
            "Select file": "בחר קובץ",
            "JSON files": "קבצי JSON",
            "Invalid file format": "פורמט קובץ לא תקין",
            "Failed to import data": "ייבוא הנתונים נכשל",
            ":Language / שפה": ":Language / שפה"  # Keep dual text for clarity
        }
        if self.language == "עברית":
            # Handle days and dynamic totals
            for day in ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]:
                if text == day:
                    return translations.get(day, text)
            if text.startswith("Total hours worked: "):
                value = text.replace("Total hours worked: ", "")
                return f"{translations['Total hours worked: ']}{value}"
            if text.startswith("Total earnings: "):
                value = text.replace("Total earnings: ", "").replace(" NIS*", "")
                return f"{translations['Total earnings: ']}{value}{translations[' NIS*']}"
            return translations.get(text, text)
        return text

    def switch_language(self, event=None):
        self.language = self.language_var.get()
        self.rebuild_ui()

    def rebuild_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_widgets()

    def update_wage(self, event=None):
        try:
            new_wage = float(self.wage_entry.get())
            if new_wage <= 0:
                raise ValueError
            self.wage_per_hour = new_wage
            self.update_table()
            self.update_totals()
        except ValueError:
            messagebox.showerror(self.translate("Invalid Wage"),
                                 self.translate("Please enter a valid positive number for the wage."))
            self.wage_entry.delete(0, tk.END)
            self.wage_entry.insert(0, str(int(self.wage_per_hour)))

    def start_edit(self, event):
        selected = self.table.selection()
        if not selected:
            return
        item = selected[0]
        column = self.table.identify_column(event.x)
        col_num = int(column.replace("#", ""))
        if col_num in (3, 4):  # Start Time (col 3) or End Time (col 4) in display (data tuple index: 2 for start, 3 for end)
            time_type = "start" if col_num == 3 else "end"
            self.edit_time_in_place(item, time_type)

    def edit_time_in_place(self, item, time_type):
        col_index = 2 if time_type == "start" else 3
        current_value = self.table.item(item, 'values')[col_index]

        def on_edit(event):
            new_time = entry.get().strip()
            try:
                datetime.strptime(new_time, "%H:%M")
            except ValueError:
                messagebox.showerror(self.translate("Invalid time"),
                                     self.translate("Please enter time in HH:MM format"))
                return
            idx = self.table.index(item)
            new_row = list(self.data[idx])
            new_row[col_index] = new_time
            new_row[4] = self.calculate_work_hours(new_row[2], new_row[3])
            new_row[5] = self.calculate_earnings(new_row[4])
            self.data[idx] = tuple(new_row)
            self.update_table()
            self.update_totals()
            entry.destroy()

        bbox = self.table.bbox(item, column=f"#{col_index+1}")
        if not bbox:
            return
        entry = ttk.Entry(self.table, justify="right")
        entry.insert(0, current_value)
        entry.select_range(0, tk.END)
        entry.focus_set()
        entry.bind("<Return>", on_edit)
        entry.bind("<FocusOut>", lambda e: entry.destroy())
        entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])

    def add_entry(self):
        date = self.date_entry.get()
        try:
            day_in_english = datetime.strptime(date, '%d/%m/%Y').strftime('%A')
        except ValueError:
            messagebox.showerror(self.translate("Invalid date"),
                                 self.translate("Please enter a valid date"))
            return

        start_time = self.start_time_entry.get().strip()
        end_time = self.end_time_entry.get().strip()

        if ":" not in start_time:
            start_time += ":00"
        if ":" not in end_time:
            end_time += ":00"
        try:
            datetime.strptime(start_time, "%H:%M")
            datetime.strptime(end_time, "%H:%M")
        except ValueError:
            messagebox.showerror(self.translate("Invalid time"),
                                 self.translate("Please enter time in HH:MM format"))
            return

        hours_worked = self.calculate_work_hours(start_time, end_time)
        earnings = self.calculate_earnings(hours_worked)
        self.data.append((date, day_in_english, start_time, end_time, hours_worked, earnings))
        self.data.sort(key=lambda x: datetime.strptime(x[0], '%d/%m/%Y'))
        self.update_table()
        self.update_totals()

    def calculate_work_hours(self, start_time, end_time):
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        if end <= start:
            end += timedelta(days=1)
        duration = end - start
        hours = duration.total_seconds() / 3600
        return round(hours, 2)

    def calculate_earnings(self, hours):
        return round(hours * self.wage_per_hour, 2)

    def update_table(self):
        for row in self.table.get_children():
            self.table.delete(row)
        for entry in self.data:
            date, day_in_english, start, end, hours, _ = entry
            day = self.translate(day_in_english)
            earnings = self.calculate_earnings(hours)
            self.table.insert("", "end", values=(date, day, start, end, hours, earnings))

    def update_totals(self):
        total_hours = sum(entry[4] for entry in self.data)
        total_earnings = sum(self.calculate_earnings(entry[4]) for entry in self.data)
        hours_text = f"Total hours worked: {total_hours:.2f}"
        earnings_text = f"Total earnings: {total_earnings:.2f} NIS*"
        self.total_hours_label.config(text=self.translate(hours_text))
        self.total_earnings_label.config(text=self.translate(earnings_text))

    def delete_entry(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning(self.translate("No Selection"),
                                   self.translate("Please select an entry to delete."))
            return
        idx = self.table.index(selected_item[0])
        del self.data[idx]
        self.update_table()
        self.update_totals()

    def load_data(self):
        try:
            if os.path.exists("work_hours_data.json"):
                with open("work_hours_data.json", "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                    self.data = loaded_data.get('entries', [])
                    self.wage_per_hour = loaded_data.get('wage_per_hour', 32)
                    self.language = loaded_data.get('language', "English")
        except (json.JSONDecodeError, KeyError) as e:
            messagebox.showerror(self.translate("Error"),
                                 f"{self.translate('Failed to load data')}: {str(e)}")

    def save_data(self):
        try:
            with open("work_hours_data.json", "w", encoding="utf-8") as f:
                json.dump({
                    'entries': self.data,
                    'wage_per_hour': self.wage_per_hour,
                    'language': self.language
                }, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror(self.translate("Error"),
                                 f"{self.translate('Failed to save data')}: {str(e)}")

    def save_data_and_exit(self):
        self.save_data()
        self.root.destroy()

    def import_data(self):
        file_path = filedialog.askopenfilename(
            title=self.translate("Select file"),
            filetypes=[(self.translate("JSON files"), "*.json")]
        )
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                imported_data = json.load(f)
                if 'entries' in imported_data:
                    self.data.extend(imported_data['entries'])
                    self.data.sort(key=lambda x: datetime.strptime(x[0], '%d/%m/%Y'))
                    self.update_table()
                    self.update_totals()
                else:
                    raise KeyError(self.translate("Invalid file format"))
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            messagebox.showerror(self.translate("Error"),
                                 f"{self.translate('Failed to import data')}: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkHoursApp(root)
    root.mainloop()
