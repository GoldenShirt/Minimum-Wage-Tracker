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
        self.load_data()

        self.create_widgets()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # Global wage per hour
        self.wage_label = tk.Label(self.root, text="Wage per hour (NIS):")
        self.wage_label.pack()
        self.wage_entry = tk.Entry(self.root)
        self.wage_entry.pack()
        self.wage_entry.insert(0, str(int(self.wage_per_hour)))
        self.wage_entry.bind("<FocusOut>", self.update_wage)
        self.wage_entry.bind("<Return>", self.update_wage)

        # Input fields to add new entry
        tk.Label(self.root, text="Date:").pack()
        self.date_entry = DateEntry(self.root, width=12, background='darkblue', foreground='white', borderwidth=2, 
                                    year=datetime.now().year, date_pattern='dd/mm/yyyy')
        self.date_entry.pack()

        tk.Label(self.root, text="Start Time:").pack()
        self.start_time_entry = tk.Entry(self.root)
        self.start_time_entry.pack()

        tk.Label(self.root, text="End Time:").pack()
        self.end_time_entry = tk.Entry(self.root)
        self.end_time_entry.pack()

        # Button frame for Add Entry and Delete Entry
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # Button to save the entry
        tk.Button(button_frame, text="Add Entry", command=self.add_entry).pack(side=tk.LEFT, padx=5)

        # Button to delete a selected entry
        tk.Button(button_frame, text="Delete Entry", command=self.delete_entry).pack(side=tk.LEFT, padx=5)

        # Table to display data
        self.table = ttk.Treeview(self.root, columns=("date", "day", "start", "end", "hours", "earnings"), show='headings')
        self.table.heading("date", text="Date")
        self.table.heading("day", text="Day")
        self.table.heading("start", text="Start Time")
        self.table.heading("end", text="End Time")
        self.table.heading("hours", text="Hours Worked")
        self.table.heading("earnings", text="Earnings (NIS)")

        for col in self.table["columns"]:
            self.table.column(col, width=100, anchor="center")

        self.table.pack(fill="both", expand=True)

        # Vertical lines between columns
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

        self.table.bind("<Double-1>", self.start_edit)

        # Labels for total hours and total earnings
        self.total_hours_label = tk.Label(self.root, text="Total hours worked: 0")
        self.total_hours_label.pack()
        self.total_earnings_label = tk.Label(self.root, text="Total earnings: 0 NIS")
        self.total_earnings_label.pack()

        # Button to import data
        tk.Button(self.root, text="Import Data", command=self.import_data).pack(pady=5)

        self.update_table()
        self.update_totals()

    def update_wage(self, event=None):
        try:
            new_wage = float(self.wage_entry.get())
            if new_wage <= 0:
                raise ValueError
            self.wage_per_hour = new_wage
            self.update_table()
            self.update_totals()
        except ValueError:
            messagebox.showerror("Invalid Wage", "Please enter a valid positive number for the wage.")
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
                messagebox.showerror("Invalid time", "Please enter time in HH:MM format")
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
            messagebox.showerror("Invalid date", "Please enter a valid date")
            return

        start_time = self.start_time_entry.get()
        end_time = self.end_time_entry.get()

        try:
            datetime.strptime(start_time, "%H:%M")
            datetime.strptime(end_time, "%H:%M")
        except ValueError:
            messagebox.showerror("Invalid time", "Please enter time in HH:MM format")
            return

        hours_worked = self.calculate_work_hours(start_time, end_time)
        earnings = self.calculate_earnings(hours_worked)
        self.data.append((date, day, start_time, end_time, hours_worked, earnings))
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

        self.total_hours_label.config(text=f"Total hours worked: {total_hours:.2f}")
        self.total_earnings_label.config(text=f"Total earnings: {total_earnings:.2f} NIS")

    def delete_entry(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an entry to delete.")
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
        except (json.JSONDecodeError, KeyError) as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")

    def save_data(self):
        try:
            with open("work_hours_data.json", "w") as f:
                json.dump({'entries': self.data, 'wage_per_hour': self.wage_per_hour}, f)
        except IOError as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")

    def on_closing(self):
        self.save_data()
        self.root.destroy()

    def import_data(self):
        file_path = filedialog.askopenfilename(title="Select file", filetypes=(("JSON files", "*.json"),))
        if file_path:
            try:
                with open(file_path, "r") as f:
                    imported_data = json.load(f)
                
                if 'entries' in imported_data and 'wage_per_hour' in imported_data:
                    self.data = []
                    for entry in imported_data['entries']:
                        if len(entry) >= 4:
                            date, day, start_time, end_time = entry[:4]
                            hours_worked = self.calculate_work_hours(start_time, end_time)
                            earnings = self.calculate_earnings(hours_worked)
                            self.data.append((date, day, start_time, end_time, hours_worked, earnings))
                    
                    self.wage_per_hour = imported_data['wage_per_hour']
                    self.wage_entry.delete(0, tk.END)
                    self.wage_entry.insert(0, str(int(self.wage_per_hour)))
                    
                    self.update_table()
                    self.update_totals()
                    messagebox.showinfo("Import Successful", "Data imported successfully")
                else:
                    raise ValueError("Invalid file format")
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                messagebox.showerror("Import Error", f"Failed to import data: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkHoursApp(root)
    root.mainloop()