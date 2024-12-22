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
        # Language selection
        self.language_var = tk.StringVar(value=self.language)
        tk.Label(self.root, text="Language / שפה:").pack()
        language_menu = ttk.Combobox(self.root, textvariable=self.language_var, state="readonly")
        language_menu['values'] = ("English", "עברית")
        language_menu.pack()
        language_menu.bind("<<ComboboxSelected>>", self.switch_language)

        # Global wage per hour
        self.wage_label = tk.Label(self.root, text=self.translate("Wage per hour (NIS):"))
        self.wage_label.pack()
        self.wage_entry = tk.Entry(self.root)
        self.wage_entry.pack()
        self.wage_entry.insert(0, str(int(self.wage_per_hour)))
        self.wage_entry.bind("<FocusOut>", self.update_wage)
        self.wage_entry.bind("<Return>", self.update_wage)

        # Input fields to add new entry
        tk.Label(self.root, text=self.translate("Date:")).pack()
        self.date_entry = DateEntry(self.root, width=12, background='darkblue', foreground='white', borderwidth=2, 
                                    year=datetime.now().year, date_pattern='dd/mm/yyyy')
        self.date_entry.pack()

        tk.Label(self.root, text=self.translate("Start Time:")).pack()
        self.start_time_entry = tk.Entry(self.root)
        self.start_time_entry.pack()

        tk.Label(self.root, text=self.translate("End Time:")).pack()
        self.end_time_entry = tk.Entry(self.root)
        self.end_time_entry.pack()

        # Button frame for Add Entry and Delete Entry
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # Button to save the entry
        tk.Button(button_frame, text=self.translate("Add Entry"), command=self.add_entry).pack(side=tk.LEFT, padx=5)

        # Button to delete a selected entry
        tk.Button(button_frame, text=self.translate("Delete Entry"), command=self.delete_entry).pack(side=tk.LEFT, padx=5)

        # Table to display data
        self.table = ttk.Treeview(self.root, columns=("date", "day", "start", "end", "hours", "earnings"), show='headings')
        self.table.heading("date", text=self.translate("Date"))
        self.table.heading("day", text=self.translate("Day"))
        self.table.heading("start", text=self.translate("Start Time"))
        self.table.heading("end", text=self.translate("End Time"))
        self.table.heading("hours", text=self.translate("Hours Worked"))
        self.table.heading("earnings", text=self.translate("Earnings (NIS)*"))

        for col in self.table["columns"]:
            self.table.column(col, width=100, anchor="center")

        self.table.pack(fill="both", expand=True)

        # Vertical lines between columns
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

        self.table.bind("<Double-1>", self.start_edit)

        # Labels for total hours and total earnings
        self.total_hours_label = tk.Label(self.root, text=self.translate("Total hours worked: 0"))
        self.total_hours_label.pack()
        self.total_earnings_label = tk.Label(self.root, text=self.translate("Total earnings: 0 NIS*"))
        self.total_earnings_label.pack()

        # Note about earnings estimation
        tk.Label(self.root, text=self.translate("* Earnings are estimations"), fg="gray").pack()

        # Button to import data
        tk.Button(self.root, text=self.translate("Import Data"), command=self.import_data).pack(pady=5)

        self.update_table()
        self.update_totals()

    def translate(self, text):
        translations = {
            "Wage per hour (NIS):": "שכר לשעה (₪):",
            "Date:": "תאריך:",
            "Start Time:": "שעת התחלה:",
            "End Time:": "שעת סיום:",
            "Add Entry": "הוסף רשומה",
            "Delete Entry": "מחק רשומה",
            "Date": "תאריך",
            "Day": "יום",
            "Start Time": "שעת התחלה",
            "End Time": "שעת סיום",
            "Hours Worked": "שעות עבודה",
            "Earnings (NIS)*": "שכר (₪)*",
            "Total hours worked: 0": "סה\"כ שעות עבודה: 0",
            "Total earnings: 0 NIS*": "סה\"כ שכר: 0 ₪*",
            "Import Data": "ייבוא נתונים",
            "* Earnings are estimations": "* השכר הוא הערכה",
        }
        if self.language == "עברית":
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
            messagebox.showerror(self.translate("Invalid Wage"), self.translate("Please enter a valid positive number for the wage."))
            self.wage_entry.delete(0, tk.END)
            self.wage_entry.insert(0, str(int(self.wage_per_hour)))

    def start_edit(self, event):
        selected_item = self.table.selection()[0]
        column = self.table.identify_column(event.x)
        col_num = int(column.replace("#", ""))

        if col_num == 3:  # Start Time
            self.edit_time_in_place(selected_item, "start")
        elif col_num == 4:  # End Time
            self.edit_time_in_place(selected_item, "end")

    def edit_time_in_place(self, item, time_type):
        col_index = 2 if time_type == "start" else 3
        current_value = self.table.item(item, 'values')[col_index]

        def on_edit(event):
            new_time = entry.get()
            try:
                datetime.strptime(new_time, "%H:%M")
            except ValueError:
                messagebox.showerror(self.translate("Invalid time"), self.translate("Please enter time in HH:MM format"))
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

        entry = tk.Entry(self.table)
        entry.insert(0, current_value)
        entry.select_range(0, tk.END)
        entry.focus_set()
        entry.bind("<Return>", on_edit)
        entry.bind("<FocusOut>", lambda e: entry.destroy())
        entry.place(x=self.table.bbox(item, column=col_index)[0],
                    y=self.table.bbox(item, column=col_index)[1],
                    width=self.table.column(col_index)['width'])

    def add_entry(self):
        date = self.date_entry.get()
        try:
            day = datetime.strptime(date, '%d/%m/%Y').strftime('%A')
        except ValueError:
            messagebox.showerror(self.translate("Invalid date"), self.translate("Please enter a valid date"))
            return

        start_time = self.start_time_entry.get()
        end_time = self.end_time_entry.get()

        try:
            if ":" not in start_time:
                start_time += ":00"
            if ":" not in end_time:
                end_time += ":00"
            datetime.strptime(start_time, "%H:%M")
            datetime.strptime(end_time, "%H:%M")
        except ValueError:
            messagebox.showerror(self.translate("Invalid time"), self.translate("Please enter time in HH:MM format"))
            return

        hours_worked = self.calculate_work_hours(start_time, end_time)
        earnings = self.calculate_earnings(hours_worked)
        self.data.append((date, day, start_time, end_time, hours_worked, earnings))
        self.data.sort(key=lambda x: datetime.strptime(x[0], '%d/%m/%Y'))  # Sort chronologically by date
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
            date, day, start, end, hours, _ = entry
            earnings = self.calculate_earnings(hours)
            self.table.insert("", "end", values=(date, day, start, end, hours, earnings))

    def update_totals(self):
        total_hours = sum(entry[4] for entry in self.data)
        total_earnings = sum(self.calculate_earnings(entry[4]) for entry in self.data)

        self.total_hours_label.config(text=self.translate(f"Total hours worked: {total_hours:.2f}"))
        self.total_earnings_label.config(text=self.translate(f"Total earnings: {total_earnings:.2f} NIS*"))

    def delete_entry(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning(self.translate("No Selection"), self.translate("Please select an entry to delete."))
            return
        idx = self.table.index(selected_item[0])
        del self.data[idx]
        self.update_table()
        self.update_totals()

    def load_data(self):
        try:
            if os.path.exists("work_hours_data.json"):
                with open("work_hours_data.json", "r") as f:
                    loaded_data = json.load(f)
                    self.data = loaded_data['entries']
                    self.wage_per_hour = loaded_data.get('wage_per_hour', 32)
                    self.language = loaded_data.get('language', "English")
        except (json.JSONDecodeError, KeyError) as e:
            messagebox.showerror(self.translate("Error"), f"{self.translate('Failed to load data')}: {str(e)}")

    def save_data(self):
        try:
            with open("work_hours_data.json", "w") as f:
                json.dump({'entries': self.data, 'wage_per_hour': self.wage_per_hour, 'language': self.language}, f)
        except Exception as e:
            messagebox.showerror(self.translate("Error"), f"{self.translate('Failed to save data')}: {str(e)}")

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
            with open(file_path, "r") as f:
                imported_data = json.load(f)
                if 'entries' in imported_data:
                    self.data.extend(imported_data['entries'])
                    self.data.sort(key=lambda x: datetime.strptime(x[0], '%d/%m/%Y'))
                    self.update_table()
                    self.update_totals()
                else:
                    raise KeyError(self.translate("Invalid file format"))
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            messagebox.showerror(self.translate("Error"), f"{self.translate('Failed to import data')}: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkHoursApp(root)
    root.mainloop()
