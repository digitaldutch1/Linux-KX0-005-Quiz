


import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import simpledialog  # For asking rename input
from PIL import Image, ImageTk
import json
import os
import sys
import webbrowser
import random

def load_questions_from_json(filename):
    """
    Loads JSON data from a file, returning the first chapter found.
    """
    try:
        # If we are frozen (PyInstaller), use the EXE folder; else use script's folder.
        if getattr(sys, 'frozen', False):
            current_directory = os.path.dirname(sys.executable)
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))

        full_path = os.path.join(current_directory, 'assets', 'linux_questions', filename)

        with open(full_path, 'r') as file:
            data = json.load(file)
            return data['chapters'][0]
    except (FileNotFoundError, json.JSONDecodeError) as e:
        messagebox.showerror("Error", f"Could not load questions: {e}")
    return {}

def get_question_count_from_json(filename):
    """
    Returns the number of questions within the specified JSON file.
    """
    try:
        if getattr(sys, 'frozen', False):
            current_directory = os.path.dirname(sys.executable)
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))

        full_path = os.path.join(current_directory, 'assets', 'linux_questions', filename)

        with open(full_path, 'r') as file:
            data = json.load(file)
            return len(data['chapters'][0]['questions'])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        messagebox.showerror("Error", f"Could not load questions: {e}")
        return 0

### CUSTOM CHUNKING LOGIC ###
def chunk_array_in_lines(arr, items_per_line=25):
    """
    Returns a string representation of a list of integers,
    chunked with up to items_per_line items per line.
    """
    if not arr:
        return "[]"

    lines = []
    chunk = []
    for i, val in enumerate(arr, start=1):
        chunk.append(str(val))
        if i % items_per_line == 0:
            lines.append(", ".join(chunk))
            chunk = []
    if chunk:
        lines.append(", ".join(chunk))

    joined_lines = []
    for i, line_content in enumerate(lines):
        # If not the last line, add a comma at end
        if i < len(lines) - 1:
            joined_lines.append("  " + line_content + ",")
        else:
            joined_lines.append("  " + line_content)

    result = "[\n" + "\n".join(joined_lines) + "\n]"
    return result
### END CUSTOM CHUNKING LOGIC ###

class QuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Linux+ KX0-005")
        self.master.geometry("1200x800")

        # Tracking and state variables
        self.current_chapter_data = None
        self.current_question_index = 0
        self.correct_answers = []
        self.user_answers = []
        self.session_active = False
        self.assessment_mode = False
        self.current_question = None
        self.current_session_title = ""

        # Holds references to info images so they won't get garbage-collected
        self.info_images = {}

        # Load custom assessments
        self.assessments = self.load_assessments()

        # Center the main window
        self.center_window_main(self.master, 1400, 800)

        # Banner label
        self.banner = tk.Label(self.master, text="Linux+ KX0-005", font=("Helvetica", 40, "bold"))
        self.banner.pack(pady=20)

        # Navigation bar container
        self.navbar_frame = tk.Frame(self.master)
        self.navbar_frame.pack()

        # ---------------- Ebook Menu ---------------
        self.ebook_menu = tk.Menubutton(
            self.navbar_frame,
            text="Ebook",
            font=("Helvetica", 26),
            relief="raised",
            borderwidth=1
        )
        self.ebook_menu.menu = tk.Menu(self.ebook_menu, tearoff=0, font=("Helvetica", 18))
        self.ebook_menu["menu"] = self.ebook_menu.menu
        self.ebook_menu.pack(side="left", padx=20)

        self.ebook_menu.menu.add_command(label="Linux +", command=self.open_ebook)
        self.ebook_menu.menu.add_command(label="Orchestration tools", command=self.open_orchestration_tools)
        self.ebook_menu.menu.add_command(label="Git & Github", command=self.open_git_github)
        self.ebook_menu.menu.add_command(label="Summary Chapter 2: Introduction to Services", command=self.open_summary_chapter_2)
        self.ebook_menu.menu.add_command(label="Summary Chapter 3: Managing Files, Directories, and Text", command=self.open_summary_chapter_3)
        self.ebook_menu.menu.add_command(label="Summary Chapter 4: Searching and Analyzing tekst", command=self.open_summary_chapter_4)
        self.ebook_menu.menu.add_command(label="Summary Chapter 5: Explaining the Boot Process", command=self.open_summary_chapter_5)
        self.ebook_menu.menu.add_command(label="Summary Chapter 6: Maintaining System Startup and Services in Linux", command=self.open_summary_chapter_6)
        self.ebook_menu.menu.add_command(label="Summary Chapter 7: Configuring Network Connections", command=self.open_summary_chapter_7)

        # ---------------- Chapters Menu ---------------
        self.chapter_menu = tk.Menubutton(
            self.navbar_frame,
            text="Chapters",
            font=("Helvetica", 26),
            relief="raised",
            borderwidth=1
        )
        self.chapter_menu.menu = tk.Menu(self.chapter_menu, tearoff=0, font=("Helvetica", 18))
        self.chapter_menu["menu"] = self.chapter_menu.menu
        self.chapter_menu.pack(side="left", padx=20)

        for i in range(2, 31):
            chapter_data = self.get_chapter_data(f"chapter{i}.json")
            chapter_title = chapter_data['description'] if chapter_data else f"Title of Chapter {i}"
            question_count = self.get_question_count(i)

            self.chapter_menu.menu.add_command(
                label=f"Chapter {i}: {chapter_title} ({question_count})",
                command=lambda i=i: self.start_quiz(f"chapter{i}.json")
            )

        # ---------------- Exercises Menu ---------------
        self.exercise_menu = tk.Menubutton(
            self.navbar_frame,
            text="Exercises",
            font=("Helvetica", 26),
            relief="raised",
            borderwidth=1
        )
        self.exercise_menu.menu = tk.Menu(self.exercise_menu, tearoff=0, font=("Helvetica", 18))
        self.exercise_menu["menu"] = self.exercise_menu.menu
        self.exercise_menu.pack(side="left", padx=20)

        exercise_chapter2_count = get_question_count_from_json("exerciseChapter2.json")
        self.exercise_menu.menu.add_command(
            label=f"Chapter 2 Introduction to Services ({exercise_chapter2_count})",
            command=lambda: self.start_exercise2("exerciseChapter2.json")
        )

        exercise_chapter3_count = get_question_count_from_json("exerciseChapter3.json")
        self.exercise_menu.menu.add_command(
            label=f"Chapter 3 Managing Files, Directories, and Text ({exercise_chapter3_count})",
            command=lambda: self.start_exercise3("exerciseChapter3.json")
        )

        exercise_chapter4_count = get_question_count_from_json("exerciseChapter4.json")
        self.exercise_menu.menu.add_command(
            label=f"Chapter 4 Searching and Analyzing Text ({exercise_chapter4_count})",
            command=lambda: self.start_exercise4("exerciseChapter4.json")
        )

        exercise_chapter5_count = get_question_count_from_json("exerciseChapter5.json")
        self.exercise_menu.menu.add_command(
            label=f"Chapter 5 Explaining the Boot Process ({exercise_chapter5_count})",
            command=lambda: self.start_exercise5("exerciseChapter5.json")
        )

        exercise_chapter6_count = get_question_count_from_json("exerciseChapter6.json")
        self.exercise_menu.menu.add_command(
            label=f"Chapter 6 Maintaining System Startup and Services in Linux ({exercise_chapter6_count})",
            command=lambda: self.start_exercise6("exerciseChapter6.json")
        )

        exercise_chapter7_count = get_question_count_from_json("exerciseChapter7.json")
        self.exercise_menu.menu.add_command(
            label=f"Chapter 7 Configuring Network Conntections ({exercise_chapter7_count})",
            command=lambda: self.start_exercise7("exerciseChapter7.json")
        )

        # ---------------- Assessment Menu ---------------
        self.assessment_menu = tk.Menubutton(
            self.navbar_frame,
            text="Assessments",
            font=("Helvetica", 26),
            relief="raised",
            borderwidth=1
        )
        self.assessment_menu.menu = tk.Menu(self.assessment_menu, tearoff=0, font=("Helvetica", 18))
        self.assessment_menu["menu"] = self.assessment_menu.menu
        self.assessment_menu.pack(side="left", padx=20)

        assessment_1_count = get_question_count_from_json("assessment1.json")
        self.assessment_menu.menu.add_command(
            label=f"Assessment 1 ({assessment_1_count})",
            command=lambda: self.start_assessment("assessment1.json")
        )

        self.assessment_menu.menu.add_command(
            label="Assessment 2 (90)",
            command=self.start_assessment2
        )

        assessment_3_count = get_question_count_from_json("assessment3.json")
        self.assessment_menu.menu.add_command(
            label=f"Assessment 3 ({assessment_3_count})",
            command=lambda: self.start_assessment3("assessment3.json")
        )

        assessment_4_count = get_question_count_from_json("assessment4.json")
        self.assessment_menu.menu.add_command(
            label=f"Assessment 4 ({assessment_4_count})",
            command=lambda: self.start_assessment4("assessment4.json")
        )

        assessment_5_count = get_question_count_from_json("assessment5.json")
        self.assessment_menu.menu.add_command(
            label=f"Assessment 5 ({assessment_5_count})",
            command=lambda: self.start_assessment5("assessment5.json")
        )

        assessment_6_count = get_question_count_from_json("assessment6.json")
        self.assessment_menu.menu.add_command(
            label=f"Assessment 6 ({assessment_6_count})",
            command=lambda: self.start_assessment6("assessment6.json")
        )

        # Custom (user-added) assessments
        self.update_assessment_menu()

        # ---------------- Edit Assessment Menu ---------------
        self.edit_assessment_menu = tk.Menubutton(
            self.navbar_frame,
            text="Edit Assessments",
            font=("Helvetica", 26),
            relief="raised",
            borderwidth=1
        )
        self.edit_assessment_menu.menu = tk.Menu(self.edit_assessment_menu, tearoff=0, font=("Helvetica", 18))
        self.edit_assessment_menu["menu"] = self.edit_assessment_menu.menu
        self.edit_assessment_menu.pack(side="left", padx=20)

        self.edit_assessment_menu.menu.add_command(label="Add Assessment", command=self.make_assessment)
        self.edit_assessment_menu.menu.add_command(label="Edit Assessments", command=self.open_edit_assessment_window)

        # ---------------- Add Questions Menu ---------------
        self.add_question_menu = tk.Menubutton(
            self.navbar_frame,
            text="Add Questions",
            font=("Helvetica", 26),
            relief="raised",
            borderwidth=1
        )
        self.add_question_menu.menu = tk.Menu(self.add_question_menu, tearoff=0, font=("Helvetica", 18))
        self.add_question_menu["menu"] = self.add_question_menu.menu
        self.add_question_menu.pack(side="left", padx=20)

        self.add_question_menu.menu.add_command(label="Add New Question", command=self.open_add_question_window)
        self.add_question_menu.menu.add_command(label="Edit Questions", command=self.open_edit_question_window)
        self.add_question_menu.menu.add_command(label="List Questions", command=self.list_questions)

        # Add main banner image below the menus
        self.add_image()

    # -------------------------------------------------------------------------
    # Helper: Center main window
    # -------------------------------------------------------------------------
    def center_window_main(self, window, w, h):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (w // 2)
        y = (screen_height // 2) - (h // 2)
        window.geometry(f"{w}x{h}+{x}+{y}")

    # -------------------------------------------------------------------------
    # Helper: Center Toplevel windows
    # -------------------------------------------------------------------------
    def center_toplevel(self, window, w=1600, h=900):
        window.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (w // 2)
        y = (screen_height // 2) - (h // 2)
        window.geometry(f"{w}x{h}+{x}+{y}")

    # -------------------------------------------------------------------------
    # Simple placeholder for listing questions
    # -------------------------------------------------------------------------
    def list_questions(self):
        messagebox.showinfo("List Questions", "Hier kun je alle vragen bekijken. (Nog niet geïmplementeerd)",
                            parent=self.master)

    # -------------------------------------------------------------------------
    # Edit Assessment Window (Manage custom assessments)
    # -------------------------------------------------------------------------
    def open_edit_assessment_window(self):
        self.assessments = self.load_assessments()
        self.edit_assessment_win = tk.Toplevel(self.master)
        self.edit_assessment_win.title("Edit Assessment")
        # Center this window
        self.center_toplevel(self.edit_assessment_win, 800, 500)

        main_frame = tk.Frame(self.edit_assessment_win)
        main_frame.pack(fill="both", expand=True)

        content_frame = tk.Frame(main_frame)
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        title_label = tk.Label(content_frame, text="Edit Assessment", font=("Helvetica", 18, "bold"))
        title_label.pack(pady=10)

        list_frame = tk.Frame(content_frame)
        list_frame.pack(padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.assessment_listbox = tk.Listbox(
            list_frame,
            width=70,
            height=10,
            font=("Helvetica", 14),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            exportselection=False
        )
        self.assessment_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.assessment_listbox.yview)

        for i, assessment in enumerate(self.assessments):
            self.assessment_listbox.insert(tk.END, assessment["title"])

        # Bind single-click to toggle selection
        self.assessment_listbox.bind("<Button-1>", self.toggle_assessment_selection, add="+")

        button_frame = tk.Frame(content_frame)
        button_frame.pack(pady=10)

        self.edit_assessment_button = tk.Button(
            button_frame,
            text="Edit Assessment",
            font=("Helvetica", 14),
            command=self.edit_selected_assessment
        )
        self.edit_assessment_button.configure(state="disabled", fg="gray")
        self.edit_assessment_button.pack(side=tk.LEFT, padx=10)

        close_button = tk.Button(
            button_frame, text="Close", font=("Helvetica", 14),
            command=self.edit_assessment_win.destroy
        )
        close_button.pack(side=tk.LEFT, padx=10)

    def toggle_assessment_selection(self, event):
        lb = event.widget
        index = lb.nearest(event.y)
        current_selection = lb.curselection()
        # If user clicked the same item again -> unselect
        if current_selection and index in current_selection:
            lb.selection_clear(index)
        else:
            lb.selection_clear(0, tk.END)
            lb.selection_set(index)
        self.on_assessment_listbox_select()
        return "break"  # stop default behavior

    def on_assessment_listbox_select(self):
        selection = self.assessment_listbox.curselection()
        if selection:
            # enable the "Edit Assessment" button
            self.edit_assessment_button.configure(state="normal", fg="black")
        else:
            # disable the "Edit Assessment" button
            self.edit_assessment_button.configure(state="disabled", fg="gray")

    def edit_selected_assessment(self):
        selection = self.assessment_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Please select an assessment first.", parent=self.edit_assessment_win)
            self.edit_assessment_win.lift()
            return

        index = selection[0]
        self.open_edit_assessment_details(index)

    def open_edit_assessment_details(self, assessment_index):
        self.assessment_to_edit_index = assessment_index
        assessment_data = self.assessments[assessment_index]
        title = assessment_data["title"]
        description = assessment_data.get("description", "")
        question_ids = assessment_data.get("questions", [])

        self.edit_assessment_details_win = tk.Toplevel(self.master)
        self.edit_assessment_details_win.title("Edit Assessment")
        # Center this window
        self.center_toplevel(self.edit_assessment_details_win, 800, 600)

        main_frame = tk.Frame(self.edit_assessment_details_win)
        main_frame.pack(fill="both", expand=True)

        content_frame = tk.Frame(main_frame)
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)

        title_label = tk.Label(content_frame, text="Edit Assessment", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(10, 0))

        tk.Label(content_frame, text="Title:", font=("Helvetica", 14)).grid(
            row=1, column=0, padx=10, pady=10, sticky="e"
        )
        self.edit_title_entry = tk.Entry(content_frame, width=50)
        self.edit_title_entry.grid(row=1, column=1, padx=10, pady=10, ipady=5, sticky="ew")
        self.edit_title_entry.insert(tk.END, title)

        tk.Label(content_frame, text="Description:", font=("Helvetica", 14)).grid(
            row=2, column=0, padx=10, pady=10, sticky="e"
        )
        self.edit_description_text = tk.Text(content_frame, height=5, width=50, font=("Helvetica", 12))
        self.edit_description_text.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        self.edit_description_text.insert(tk.END, description)

        self.edit_add_question_button = tk.Button(
            content_frame, text="Add Question", command=self.open_add_questions_window_for_edit
        )
        self.edit_add_question_button.grid(row=3, column=0, columnspan=2, pady=10)

        tk.Label(content_frame, text="Selected Questions:", font=("Helvetica", 14)).grid(
            row=4, column=0, padx=10, pady=(10, 5), sticky="e"
        )
        self.edit_selected_questions_listbox = tk.Listbox(content_frame, width=70, height=10, selectmode=tk.MULTIPLE)
        self.edit_selected_questions_listbox.grid(row=4, column=1, padx=10, pady=(10, 5), sticky="ew")

        self.edit_delete_selected_questions_btn = tk.Button(
            content_frame,
            text="🗑️ Delete Selected Questions",
            command=self.delete_selected_questions_for_edit
        )
        self.edit_delete_selected_questions_btn.grid(row=5, column=0, columnspan=2, pady=(10, 0))

        self.populate_questions_in_edit_listbox(question_ids)

        button_frame = tk.Frame(content_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=15)

        edit_btn = tk.Button(button_frame, text="Save Changes", font=("Helvetica", 12), command=self.confirm_edit_assessment)
        edit_btn.pack(side=tk.LEFT, padx=10)

        delete_btn = tk.Button(button_frame, text="Delete Assessment", font=("Helvetica", 12), command=self.confirm_delete_assessment)
        delete_btn.pack(side=tk.LEFT, padx=10)

        close_btn = tk.Button(button_frame, text="Close", font=("Helvetica", 12), command=self.close_edit_assessment_details)
        close_btn.pack(side=tk.LEFT, padx=10)

    def populate_questions_in_edit_listbox(self, question_ids):
        self.edit_selected_questions_listbox.delete(0, tk.END)

        if getattr(sys, 'frozen', False):
            current_directory = os.path.dirname(sys.executable)
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))

        questions_file = os.path.join(current_directory, 'assets', 'linux_questions', 'addedQuestions.json')

        try:
            with open(questions_file, 'r') as f:
                data = json.load(f)
                all_questions = data['chapters'][0]['questions']

            question_dict = {}
            for q in all_questions:
                q_num = q['number']
                q_text = q['question']
                question_dict[q_num] = q_text

            for qid in sorted(question_ids):
                if qid in question_dict:
                    display_text = f"Nr. {qid}: {question_dict[qid]}"
                else:
                    display_text = f"Nr. {qid}: [Unknown Question]"
                self.edit_selected_questions_listbox.insert(tk.END, display_text)
        except Exception as e:
            self.show_error_message(f"Could not load existing questions: {e}")

    def open_add_questions_window_for_edit(self):
        self.edit_add_questions_win = tk.Toplevel(self.edit_assessment_details_win)
        self.edit_add_questions_win.title("Add Questions to Assessment")
        self.center_toplevel(self.edit_add_questions_win, 600, 400)

        listbox_frame = tk.Frame(self.edit_add_questions_win)
        listbox_frame.pack(pady=10)

        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        self.edit_question_listbox = tk.Listbox(
            listbox_frame,
            font=("Helvetica", 12),
            width=50,
            height=15,
            selectmode=tk.MULTIPLE
        )
        self.edit_question_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.edit_question_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_questions_for_adding_in_edit()

        add_btn = tk.Button(self.edit_add_questions_win, text="Add to Assessment", command=self.add_selected_questions_for_edit)
        add_btn.pack(pady=10)

    def load_questions_for_adding_in_edit(self):
        """
        Als addedQuestions.json geen enkele vraag bevat, tonen we i.p.v. een lege lijst
        het bericht 'First add question via "Add Questions"'
        """
        if getattr(sys, 'frozen', False):
            current_directory = os.path.dirname(sys.executable)
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))

        file_path = os.path.join(current_directory, 'assets', 'linux_questions', 'addedQuestions.json')

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                questions = data['chapters'][0]['questions']

            if not questions:
                self.edit_question_listbox.insert(tk.END, '                     First add question via "Add Questions"')
                self.edit_question_listbox.configure(state='disabled')
                return

            for question in questions:
                display_text = f"Nr. {question['number']}: {question['question']}"
                self.edit_question_listbox.insert(tk.END, display_text)

        except Exception as e:
            self.show_error_message(f"Could not load questions for adding (Edit): {e}")

    def add_selected_questions_for_edit(self):
        selected_indices = self.edit_question_listbox.curselection()
        for idx in selected_indices:
            question_display_text = self.edit_question_listbox.get(idx)

            existing_items = self.edit_selected_questions_listbox.get(0, tk.END)
            if question_display_text in existing_items:
                messagebox.showwarning(
                    "Duplicate Question",
                    f"The question:\n\n{question_display_text}\n\nAlready in the Assessment.",
                    parent=self.edit_add_questions_win
                )
                self.edit_assessment_details_win.lift()
            else:
                self.edit_selected_questions_listbox.insert(tk.END, question_display_text)

        self.edit_add_questions_win.destroy()

    def close_edit_assessment_details(self):
        self.edit_assessment_details_win.destroy()
        if hasattr(self, 'edit_assessment_win') and self.edit_assessment_win:
            self.edit_assessment_win.lift()

    def delete_selected_questions_for_edit(self):
        selected_indices = self.edit_selected_questions_listbox.curselection()
        if not selected_indices:
            self.show_error_message("Please select questions to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Would you like to delete the selected questions?",
                               parent=self.edit_assessment_details_win):
            for idx in reversed(selected_indices):
                self.edit_selected_questions_listbox.delete(idx)
            messagebox.showinfo("Success", "Selected questions deleted successfully!",
                                parent=self.edit_assessment_details_win)
            self.edit_assessment_details_win.lift()
            self.center_toplevel(self.edit_assessment_details_win, 800, 600)

    def confirm_edit_assessment(self):
        if messagebox.askyesno("Confirm", "Save changes to this assessment?", parent=self.edit_assessment_details_win):
            self.update_assessment_in_json()
            self.edit_assessment_details_win.destroy()
            if hasattr(self, 'edit_assessment_win') and self.edit_assessment_win:
                self.edit_assessment_win.destroy()
            self.open_edit_assessment_window()
            self.assessments = self.load_assessments()
            self.update_assessment_menu()

    def confirm_delete_assessment(self):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this assessment entirely?",
                               parent=self.edit_assessment_details_win):
            self.delete_assessment_in_json()
            self.edit_assessment_details_win.destroy()
            if hasattr(self, 'edit_assessment_win') and self.edit_assessment_win:
                self.edit_assessment_win.destroy()
            self.open_edit_assessment_window()
            self.assessments = self.load_assessments()
            self.update_assessment_menu()

    def update_assessment_in_json(self):
        idx = self.assessment_to_edit_index
        if idx >= len(self.assessments):
            self.show_error_message("Could not find the assessment to edit.")
            return

        new_title = self.edit_title_entry.get().strip()
        new_description = self.edit_description_text.get("1.0", tk.END).strip()

        if not new_title or not new_description:
            self.show_error_message("Title and Description cannot be empty.")
            return

        updated_questions = []
        for i in range(self.edit_selected_questions_listbox.size()):
            line = self.edit_selected_questions_listbox.get(i)
            number_part = line.split(":")[0].replace("Nr. ", "").strip()
            try:
                q_num = int(number_part)
                updated_questions.append(q_num)
            except:
                pass

        self.assessments[idx]["title"] = new_title
        self.assessments[idx]["description"] = new_description
        self.assessments[idx]["questions"] = updated_questions
        self.assessments[idx]["questions_count"] = len(updated_questions)

        self.save_assessments_to_json()
        messagebox.showinfo("Success", f"Assessment '{new_title}' updated successfully!",
                            parent=self.master)

    def delete_assessment_in_json(self):
        idx = self.assessment_to_edit_index
        if idx < 0 or idx >= len(self.assessments):
            self.show_error_message("Could not find the assessment to delete.")
            return

        deleted_title = self.assessments[idx]["title"]
        del self.assessments[idx]

        self.save_assessments_to_json()
        messagebox.showinfo("Success", f"Assessment '{deleted_title}' deleted successfully!",
                            parent=self.master)

    ### CUSTOM CODE TO SAVE ASSESSMENTS WITH CHUNKED QUESTIONS ARRAY ###
    def save_assessments_to_json(self):
        """
        Saves self.assessments to addedAssessments.json with custom chunking.
        """
        try:
            if getattr(sys, 'frozen', False):
                current_directory = os.path.dirname(sys.executable)
            else:
                current_directory = os.path.dirname(os.path.abspath(__file__))

            full_path = os.path.join(current_directory, 'assets', 'linux_questions', 'addedAssessments.json')

            items = []
            for assessment in self.assessments:
                temp_dict = dict(assessment)
                questions_list = temp_dict.pop("questions", [])
                placeholder = "###QUESTIONS_PLACEHOLDER###"
                temp_dict["questions"] = placeholder
                partial_json = json.dumps(temp_dict, indent=4)
                chunked_str = chunk_array_in_lines(questions_list, 25)
                partial_json = partial_json.replace('"###QUESTIONS_PLACEHOLDER###"', chunked_str)
                items.append(partial_json)

            final_text = "[\n" + ",\n".join(items) + "\n]\n"

            with open(full_path, 'w') as file:
                file.write(final_text)

        except Exception as e:
            self.show_error_message(f"Could not save assessments: {e}")
    ### END CUSTOM CODE ###

    # -------------------------------------------------------------------------
    # Place the main banner image on the window
    # -------------------------------------------------------------------------
    def add_image(self):
        try:
            if getattr(sys, 'frozen', False):
                current_directory = os.path.dirname(sys.executable)
            else:
                current_directory = os.path.dirname(os.path.abspath(__file__))

            image_path = os.path.join(current_directory, 'assets', 'icon', 'linux afbeelding 2.png')

            self.main_banner_img = tk.PhotoImage(file=image_path)
            self.main_image_label = tk.Label(self.master, image=self.main_banner_img)
            self.main_image_label.pack(pady=(50, 20))

        except Exception as e:
            messagebox.showerror("Error", f"Could not load main banner image: {e}",
                                 parent=self.master)

    # -------------------------------------------------------------------------
    # E-book openers
    # -------------------------------------------------------------------------
    def open_ebook(self):
        self.open_pdf_in_browser('linuxbook.pdf')

    def open_orchestration_tools(self):
        self.open_pdf_in_browser('Orchestration tools.pdf')

    def open_git_github(self):
        self.open_pdf_in_browser('Git & Github.pdf')

    def open_summary_chapter_2(self):
        self.open_pdf_in_browser('Chapter 2 introduction to services.pdf')

    def open_summary_chapter_3(self):
        self.open_pdf_in_browser('Chapter 3 Managing Files, Directories, and Tekst.pdf')

    def open_summary_chapter_4(self):
        self.open_pdf_in_browser('Chapter 4 Searching and Analyzing tekst.pdf')

    def open_summary_chapter_5(self):
        self.open_pdf_in_browser('Chapter 5 Explaining the Boot Process.pdf')

    def open_summary_chapter_6(self):
        self.open_pdf_in_browser('Chapter 6 Maintaining System Startup and Services in Linux.pdf')

    def open_summary_chapter_7(self):
        self.open_pdf_in_browser('Chapter 7 Configuring Network Connections.pdf')

    def open_pdf_in_browser(self, filename):
        if getattr(sys, 'frozen', False):
            current_directory = os.path.dirname(sys.executable)
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))

        pdf_path = os.path.join(current_directory, 'assets', 'linuxbook', filename)
        if os.path.exists(pdf_path):
            webbrowser.open(pdf_path)
        else:
            self.show_error_message(f"{filename} not found.")

    # -------------------------------------------------------------------------
    # CREATE a new custom Assessment
    # -------------------------------------------------------------------------
    def make_assessment(self):
        self.assessment_win = tk.Toplevel(self.master)
        self.assessment_win.title("Create New Assessment")
        self.center_toplevel(self.assessment_win, 700, 600)

        main_frame = tk.Frame(self.assessment_win)
        main_frame.pack(fill="both", expand=True)

        content_frame = tk.Frame(main_frame)
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)

        title_label = tk.Label(content_frame, text="Create Assessment", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(10, 0))

        tk.Label(content_frame, text="Title:", font=("Helvetica", 14)).grid(
            row=1, column=0, padx=10, pady=10, sticky="e"
        )
        self.title_entry = tk.Entry(content_frame, width=50)
        self.title_entry.grid(row=1, column=1, padx=10, pady=10, ipady=5, sticky="ew")

        tk.Label(content_frame, text="Description:", font=("Helvetica", 14)).grid(
            row=2, column=0, padx=10, pady=10, sticky="e"
        )
        self.description_entry = tk.Text(content_frame, height=5, width=50, font=("Helvetica", 12))
        self.description_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        self.add_question_button = tk.Button(content_frame, text="Add Question", command=self.open_add_questions_window)
        self.add_question_button.grid(row=3, column=0, columnspan=2, pady=10)

        tk.Label(content_frame, text="Selected Questions:", font=("Helvetica", 14)).grid(
            row=4, column=0, padx=10, pady=(10, 5), sticky="e"
        )
        self.selected_questions_listbox = tk.Listbox(content_frame, width=70, height=10, selectmode=tk.MULTIPLE)
        self.selected_questions_listbox.grid(row=4, column=1, padx=10, pady=(10, 5), sticky="ew")

        self.delete_selected_questions_button = tk.Button(
            content_frame,
            text="🗑️ Delete Selected Questions",
            command=self.delete_selected_questions
        )
        self.delete_selected_questions_button.grid(row=5, column=0, columnspan=2, pady=(10, 0))

        self.create_assessment_btn = tk.Button(content_frame, text="Create", command=self.save_assessment)
        self.create_assessment_btn.grid(row=6, column=0, columnspan=2, pady=10)

    def open_add_questions_window(self):
        self.add_questions_win = tk.Toplevel(self.master)
        self.add_questions_win.title("Add Questions to Assessment")
        self.center_toplevel(self.add_questions_win, 600, 600)

        listbox_frame = tk.Frame(self.add_questions_win)
        listbox_frame.pack(pady=10)

        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        self.question_listbox = tk.Listbox(
            listbox_frame,
            font=("Helvetica", 12),
            width=50,
            height=15,
            selectmode=tk.MULTIPLE
        )
        self.question_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.question_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_questions_for_adding()

        add_to_assessment_button = tk.Button(
            self.add_questions_win,
            text="Add to Assessment",
            command=self.add_selected_questions
        )
        add_to_assessment_button.pack(pady=10)

    def load_questions_for_adding(self):
        """
        Als addedQuestions.json geen enkele vraag bevat, tonen we hier i.p.v. een lege lijst
        het bericht 'First add question via "Add Questions"'
        """
        if getattr(sys, 'frozen', False):
            current_directory = os.path.dirname(sys.executable)
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))

        file_path = os.path.join(current_directory, 'assets', 'linux_questions', 'addedQuestions.json')

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                questions = data['chapters'][0]['questions']

            if not questions:
                self.question_listbox.insert(tk.END, '                     First add question via "Add Questions"')
                self.question_listbox.configure(state='disabled')
                return

            for question in questions:
                display_text = f"Nr. {question['number']}: {question['question']}"
                self.question_listbox.insert(tk.END, display_text)

        except Exception as e:
            self.show_error_message(f"Could not load questions for adding: {e}")

    def add_selected_questions(self):
        selected_indices = self.question_listbox.curselection()
        for index in selected_indices:
            question_display_text = self.question_listbox.get(index)

            existing_items = self.selected_questions_listbox.get(0, tk.END)
            if question_display_text in existing_items:
                messagebox.showwarning(
                    "Duplicate Question",
                    f"The question:\n\n{question_display_text}\n\nAlready in the list.",
                    parent=self.add_questions_win
                )
                self.assessment_win.lift()
            else:
                self.selected_questions_listbox.insert(tk.END, question_display_text)

        self.add_questions_win.destroy()

    def delete_selected_questions(self):
        selected_indices = self.selected_questions_listbox.curselection()
        if not selected_indices:
            self.show_error_message("Please select questions to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Would you like to delete the selected questions?",
                               parent=self.assessment_win):
            for index in reversed(selected_indices):
                self.selected_questions_listbox.delete(index)
            messagebox.showinfo("Success", "Selected questions deleted successfully!",
                                parent=self.assessment_win)

    def save_assessment(self):
        title = self.title_entry.get().strip()
        description = self.description_entry.get("1.0", tk.END).strip()

        selected_questions = []
        for i in range(self.selected_questions_listbox.size()):
            item = self.selected_questions_listbox.get(i)
            number_part = item.split(":")[0].replace("Nr. ", "").strip()
            try:
                q_num = int(number_part)
                selected_questions.append(q_num)
            except:
                pass

        if not title or not description:
            self.show_error_message("Title and Description cannot be empty.")
            return

        assessment_data = {
            "chapter": "Custom Assessment",
            "title": title,
            "description": description,
            "questions": selected_questions,
            "questions_count": len(selected_questions)
        }

        self.assessments.append(assessment_data)
        self.update_assessment_json()

        messagebox.showinfo("Success", "Assessment created successfully!",
                            parent=self.assessment_win)
        self.update_assessment_menu()
        self.assessment_win.destroy()

    def update_assessment_json(self):
        try:
            if getattr(sys, 'frozen', False):
                current_directory = os.path.dirname(sys.executable)
            else:
                current_directory = os.path.dirname(os.path.abspath(__file__))

            full_path = os.path.join(current_directory, 'assets', 'linux_questions', 'addedAssessments.json')
            # We'll just call our custom saver
            self.save_assessments_to_json()

        except Exception as e:
            self.show_error_message(f"Could not save assessments: {e}")

    def load_assessments(self):
        try:
            if getattr(sys, 'frozen', False):
                current_directory = os.path.dirname(sys.executable)
            else:
                current_directory = os.path.dirname(os.path.abspath(__file__))

            full_path = os.path.join(current_directory, 'assets', 'linux_questions', 'addedAssessments.json')

            if not os.path.exists(full_path):
                with open(full_path, 'w') as file:
                    json.dump([], file)

            with open(full_path, 'r') as file:
                data = json.load(file)
                return data
        except Exception:
            return []

    def update_assessment_menu(self):
        static_items_end_index = 6
        end_index = self.assessment_menu.menu.index('end')

        # Remove old dynamically-added items first (anything beyond the static 6)
        if end_index is not None and end_index >= static_items_end_index:
            for index in range(static_items_end_index, end_index + 1):
                self.assessment_menu.menu.delete(static_items_end_index)

        for assessment in self.assessments:
            title = assessment["title"]
            questions_count = assessment.get("questions_count", 0)
            self.assessment_menu.menu.add_command(
                label=f"{title} ({questions_count})",
                command=lambda title=title: self.start_assessment_custom(title)
            )

    def start_assessment_custom(self, title):
        matching_assessment = next((a for a in self.assessments if a["title"] == title), None)
        if not matching_assessment:
            self.show_error_message(f"No assessment found with title '{title}'.")
            return

        question_ids = matching_assessment.get("questions", [])
        if not question_ids:
            self.show_error_message(f"No questions found in assessment '{title}'.")
            return

        questions_data = self.load_questions_by_ids(question_ids)
        if not questions_data:
            self.show_error_message(f"Could not load questions for assessment '{title}'.")
            return

        self.current_chapter_data = {
            "chapter": "Custom Assessment",
            "description": title,
            "questions": questions_data
        }

        self.reset_statistics()
        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)

        self.shuffled_options = []
        for question in self.questions:
            opts = list(question["options"])
            random.shuffle(opts)
            self.shuffled_options.append(opts)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = True
        self.current_session_title = f"Assessment: {title}"

        self.question_window()

    def load_questions_by_ids(self, question_ids):
        if getattr(sys, 'frozen', False):
            current_directory = os.path.dirname(sys.executable)
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))

        file_path = os.path.join(current_directory, 'assets', 'linux_questions', 'addedQuestions.json')

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                all_questions = data['chapters'][0]['questions']
        except Exception as e:
            self.show_error_message(f"Could not open addedQuestions.json: {e}")
            return []

        question_dict = {q["number"]: q for q in all_questions}

        result_questions = []
        for qid in question_ids:
            if qid in question_dict:
                result_questions.append(question_dict[qid])
        return result_questions

    # -------------------------------------------------------------------------
    # CHAPTER HELPER
    # -------------------------------------------------------------------------
    def get_chapter_data(self, filename):
        if getattr(sys, 'frozen', False):
            current_directory = os.path.dirname(sys.executable)
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))

        full_path = os.path.join(current_directory, 'assets', 'linux_questions', filename)
        try:
            with open(full_path, 'r') as file:
                data = json.load(file)
                return data['chapters'][0]
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def get_question_count(self, chapter_number):
        try:
            path = os.path.join('assets', 'linux_questions', f"chapter{chapter_number}.json")
            with open(path, 'r') as file:
                data = json.load(file)
                return len(data['chapters'][0]['questions'])
        except (FileNotFoundError, json.JSONDecodeError):
            return 0

    # -------------------------------------------------------------------------
    # START QUIZ / EXERCISE / ASSESSMENT
    # -------------------------------------------------------------------------
    def start_quiz(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            self.show_error_message("Geen vragen gevonden in het geselecteerde hoofdstuk.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)

        self.shuffled_options = []
        for question in self.questions:
            opts = list(question["options"])
            random.shuffle(opts)
            self.shuffled_options.append(opts)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = False

        chapter_number = self.current_chapter_data.get('chapter', 'Unknown')
        chapter_title = self.current_chapter_data.get('description', 'Unknown Chapter')
        self.current_session_title = f"Chapter {chapter_number}: {chapter_title}"

        self.question_window()

    def start_assessment(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            self.show_error_message("Geen vragen gevonden in de geselecteerde beoordeling.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)

        self.shuffled_options = []
        for question in self.questions:
            opts = list(question["options"])
            random.shuffle(opts)
            self.shuffled_options.append(opts)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = True
        self.current_session_title = "Assessment 1 Questions"

        self.question_window()

    def start_assessment2(self):
        self.reset_statistics()
        filename = os.path.join('assets', 'linux_questions', "assessment2.json")
        try:
            with open(filename, 'r') as file:
                data = json.load(file)

            if 'chapters' not in data or len(data['chapters']) == 0:
                self.show_error_message("'chapters' key not found in the JSON file.")
                return

            questions = data['chapters'][0]['questions']

            if len(questions) < 90:
                self.show_error_message("Niet genoeg vragen beschikbaar in assessment2.")
                return

            self.questions = random.sample(questions, 90)
            random.shuffle(self.questions)

            self.shuffled_options = []
            for question in self.questions:
                opts = list(question["options"])
                random.shuffle(opts)
                self.shuffled_options.append(opts)

            self.current_question_index = 0
            self.user_answers = [None] * len(self.questions)
            self.session_active = True
            self.assessment_mode = True
            self.current_session_title = "Assessment 2 Questions"

            self.question_window()
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.show_error_message(f"Could not load assessment2: {e}")

    def start_assessment3(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            self.show_error_message("Geen vragen gevonden in de geselecteerde beoordeling.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)

        self.shuffled_options = []
        for question in self.questions:
            opts = list(question["options"])
            random.shuffle(opts)
            self.shuffled_options.append(opts)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = True
        self.current_session_title = "Assessment 3 Questions"

        self.question_window()

    def start_assessment4(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            self.show_error_message("Geen vragen gevonden in de geselecteerde beoordeling.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)

        self.shuffled_options = []
        for question in self.questions:
            opts = list(question["options"])
            random.shuffle(opts)
            self.shuffled_options.append(opts)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = True
        self.current_session_title = "Assessment 4 Questions"

        self.question_window()

    def start_assessment5(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            self.show_error_message("Geen vragen gevonden in de geselecteerde beoordeling.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)

        self.shuffled_options = []
        for question in self.questions:
            opts = list(question["options"])
            random.shuffle(opts)
            self.shuffled_options.append(opts)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = True
        self.current_session_title = "Assessment 5 Questions"

        self.question_window()

    def start_assessment6(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            self.show_error_message("Geen vragen gevonden in de geselecteerde beoordeling.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)

        self.shuffled_options = []
        for question in self.questions:
            opts = list(question["options"])
            random.shuffle(opts)
            self.shuffled_options.append(opts)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = True
        self.current_session_title = "Assessment 6 Questions"

        self.question_window()

    def start_exercise2(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            self.show_error_message("No questions found in Exercise Chapter 2.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)

        self.shuffled_options = []
        for question in self.questions:
            opts = list(question["options"])
            random.shuffle(opts)
            self.shuffled_options.append(opts)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = False

        chapter_number = self.current_chapter_data.get('chapter', '2')
        chapter_title = self.current_chapter_data.get('description', 'Introduction to Services')
        self.current_session_title = f"Exercise Chapter {chapter_number}: {chapter_title}"

        self.question_window()

    def start_exercise3(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            self.show_error_message("No questions found in Exercise Chapter 3.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)

        self.shuffled_options = []
        for question in self.questions:
            opts = list(question["options"])
            random.shuffle(opts)
            self.shuffled_options.append(opts)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = False

        chapter_number = self.current_chapter_data.get('chapter', '3')
        chapter_title = self.current_chapter_data.get('description', 'Managing Files, Directories, and Text')
        self.current_session_title = f"Exercise Chapter {chapter_number}: {chapter_title}"

        self.question_window()

    def start_exercise4(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            self.show_error_message("No questions found in Exercise Chapter 4.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)

        self.shuffled_options = []
        for question in self.questions:
            opts = list(question["options"])
            random.shuffle(opts)
            self.shuffled_options.append(opts)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = False

        chapter_number = self.current_chapter_data.get('chapter', '4')
        chapter_title = self.current_chapter_data.get('description', 'Searching and Analyzing Text')
        self.current_session_title = f"Exercise Chapter {chapter_number}: {chapter_title}"

        self.question_window()

    def start_exercise5(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            self.show_error_message("No questions found in Exercise Chapter 5.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)

        self.shuffled_options = []
        for question in self.questions:
            opts = list(question["options"])
            random.shuffle(opts)
            self.shuffled_options.append(opts)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = False

        chapter_number = self.current_chapter_data.get('chapter', '5')
        chapter_title = self.current_chapter_data.get('description', 'Explaining the Boot Process')
        self.current_session_title = f"Exercise Chapter {chapter_number}: {chapter_title}"

        self.question_window()

    def start_exercise6(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            self.show_error_message("No questions found in Exercise Chapter 6.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)

        self.shuffled_options = []
        for question in self.questions:
            opts = list(question["options"])
            random.shuffle(opts)
            self.shuffled_options.append(opts)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = False

        chapter_number = self.current_chapter_data.get('chapter', '6')
        chapter_title = self.current_chapter_data.get('description', 'Maintainng System Startup and Services')
        self.current_session_title = f"Exercise Chapter {chapter_number}: {chapter_title}"

        self.question_window()

    def start_exercise7(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            self.show_error_message("No questions found in Exercise Chapter 7.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)

        self.shuffled_options = []
        for question in self.questions:
            opts = list(question["options"])
            random.shuffle(opts)
            self.shuffled_options.append(opts)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = False

        chapter_number = self.current_chapter_data.get('chapter', '7')
        chapter_title = self.current_chapter_data.get('description', 'Configuring Network Connections')
        self.current_session_title = f"Exercise Chapter {chapter_number}: {chapter_title}"

        self.question_window()

    # -------------------------------------------------------------------------
    # QUIZ UI with SCROLL + Pijlen (like review_window)
    # -------------------------------------------------------------------------
    def question_window(self, title=None):
        """
        Creates the quiz window with scrolling if needed, plus arrow indicators.
        """
        self.question_win = tk.Toplevel(self.master)
        self.question_win.title("Quiz")
        self.center_toplevel(self.question_win, 1600, 900)
        self.question_win.protocol("WM_DELETE_WINDOW", self.close_question_window)

        container = tk.Frame(self.question_win)
        container.pack(fill="both", expand=True)

        self.question_canvas = tk.Canvas(container)
        self.question_canvas.pack(side="left", fill="both", expand=True)

        self.question_scrollbar = tk.Scrollbar(container, orient="vertical", command=self.question_canvas.yview)
        self.question_canvas.configure(yscrollcommand=self.question_scrollbar.set)

        self.question_content_frame = tk.Frame(self.question_canvas)

        if self.current_chapter_data.get("chapter") == "Custom Assessment":
            offset_x = 550
        else:
            offset_x = 400

        self.question_canvas.create_window((offset_x, 0), window=self.question_content_frame, anchor="nw")

        self.question_content_frame.bind("<Configure>", self._configure_question_content)

        self.q_arrow_up_label = tk.Label(container, text="⬆", font=("Helvetica", 32, "bold"), fg="black")
        self.q_arrow_down_label = tk.Label(container, text="⬇", font=("Helvetica", 32, "bold"), fg="black")

        self.question_canvas.bind_all("<MouseWheel>", self._on_mousewheel_question)

        bottom_frame = tk.Frame(self.question_win)
        bottom_frame.pack(side="bottom", pady=(30, 30))

        self.chapter_title_label = tk.Label(
            self.question_content_frame,
            text="",
            font=("Helvetica", 24, "bold"),
            justify="center"
        )
        self.chapter_title_label.pack(pady=10)

        self.question_counter = tk.Label(
            self.question_content_frame,
            text="",
            font=("Helvetica", 18),
            justify="center"
        )
        self.question_counter.pack(pady=10)

        self.question_label = tk.Label(
            self.question_content_frame,
            text="",
            wraplength=900,
            font=("Helvetica", 18),
            justify="center"
        )
        self.question_label.pack(pady=15)

        self.options_frame = tk.Frame(self.question_content_frame)
        self.options_frame.pack(pady=15)

        self.submit_button = tk.Button(bottom_frame, text="Submit", font=("Helvetica", 16), command=self.submit_answer)
        self.submit_button.pack(side="top", pady=(0, 30))

        nav_btns_frame = tk.Frame(bottom_frame)
        nav_btns_frame.pack()

        self.previous_button = tk.Button(nav_btns_frame, text="Previous", font=("Helvetica", 16), command=self.previous_question)
        self.previous_button.pack(side="left", padx=15)

        self.stop_button = tk.Button(nav_btns_frame, text="Stop", font=("Helvetica", 16), command=self.show_stats)
        self.stop_button.pack(side="left", padx=15)

        self.exit_button = tk.Button(nav_btns_frame, text="Exit", font=("Helvetica", 16), command=self.exit_quiz)
        self.exit_button.pack(side="left", padx=15)

        self.next_button = tk.Button(nav_btns_frame, text="Next", font=("Helvetica", 16), command=self.next_question)
        self.next_button.pack(side="left", padx=15)

        self.load_question_canvas()

    def _configure_question_content(self, event):
        self.question_canvas.configure(scrollregion=self.question_canvas.bbox("all"))

        content_height = self.question_content_frame.winfo_reqheight()
        canvas_height = self.question_canvas.winfo_height()

        if content_height > canvas_height:
            self.question_scrollbar.pack(side="right", fill="y")
            self.question_canvas.bind_all("<MouseWheel>", self._on_mousewheel_question)
        else:
            self.question_scrollbar.pack_forget()
            self.question_canvas.unbind_all("<MouseWheel>")

        self._update_question_arrows()

    def _on_mousewheel_question(self, event):
        self.question_canvas.yview_scroll(int(-1*(event.delta / 120)), "units")
        self._update_question_arrows()

    def _update_question_arrows(self):
        top_frac, bottom_frac = self.question_canvas.yview()
        container = self.question_canvas.master

        container_width = container.winfo_width()
        container_height = container.winfo_height()

        x_position = container_width - 60
        y_down = container_height - 30
        y_up = y_down - 60

        if top_frac > 0:
            self.q_arrow_up_label.place(x=x_position, y=y_up, anchor="center")
        else:
            self.q_arrow_up_label.place_forget()

        if bottom_frac < 1:
            self.q_arrow_down_label.place(x=x_position, y=y_down, anchor="center")
        else:
            self.q_arrow_down_label.place_forget()

    def load_question_canvas(self):
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        for child in self.question_content_frame.winfo_children():
            if isinstance(child, tk.Label) and getattr(child, 'image', None):
                child.destroy()

        self.chapter_title_label.pack_forget()
        self.question_counter.pack_forget()
        self.question_label.pack_forget()
        self.options_frame.pack_forget()

        self.chapter_title_label.pack(pady=10)
        self.question_counter.pack(pady=10)
        self.question_label.pack(pady=15)
        self.options_frame.pack(pady=15)

        self.chapter_title_label.config(text=self.current_session_title)
        self.question_counter.config(text=f"Question {self.current_question_index + 1} / {len(self.questions)}")
        self.question_label.config(text=self.questions[self.current_question_index]["question"])

        self.display_question_image_canvas()

        options = self.shuffled_options[self.current_question_index]
        saved_answers = self.user_answers[self.current_question_index]
        self.var_list = []

        for index, option in enumerate(options):
            previously_selected = (index in saved_answers) if saved_answers is not None else False
            var = tk.BooleanVar(value=previously_selected)
            checkbox = tk.Checkbutton(self.options_frame, text=option, variable=var, font=("Helvetica", 18))
            checkbox.pack(anchor="w")
            self.var_list.append(var)

        self._update_question_arrows()

    def display_question_image_canvas(self):
        question = self.questions[self.current_question_index]
        image_path = question.get("image")
        if image_path:
            if not os.path.isabs(image_path):
                full_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.normpath(image_path))
            else:
                full_image_path = os.path.normpath(image_path)

            if os.path.exists(full_image_path):
                try:
                    image = Image.open(full_image_path)
                    max_width = 800
                    max_height = 600
                    orig_w, orig_h = image.size
                    scale_factor = min(max_width / orig_w, max_height / orig_h)

                    if scale_factor < 1:
                        new_w = int(orig_w * scale_factor)
                        new_h = int(orig_h * scale_factor)
                        image = image.resize((new_w, new_h), Image.LANCZOS)

                    self.question_img = ImageTk.PhotoImage(image)
                    self.question_img_label = tk.Label(self.question_content_frame, image=self.question_img)
                    self.question_img_label.image = self.question_img
                    self.question_img_label.pack(before=self.options_frame, pady=10)
                except Exception as e:
                    print(f"Could not load/resize image: {e}")

    def previous_question(self):
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.load_question_canvas()

    def next_question(self):
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.load_question_canvas()
        else:
            self.show_stats()

    def submit_answer(self):
        selected_answers = [index for index, var in enumerate(self.var_list) if var.get()]
        self.user_answers[self.current_question_index] = selected_answers

        correct_answer = self.questions[self.current_question_index]["answer"]
        if isinstance(correct_answer, list):
            correct_answer_indices = [
                self.shuffled_options[self.current_question_index].index(ans) for ans in correct_answer
            ]
            num_correct_selected = len(set(correct_answer_indices).intersection(selected_answers))
            num_correct_answers = len(correct_answer)
            score = num_correct_selected / num_correct_answers
            self.correct_answers.append(score)
        else:
            correct_index = self.shuffled_options[self.current_question_index].index(correct_answer)
            if selected_answers == [correct_index]:
                self.correct_answers.append(1.0)
            else:
                self.correct_answers.append(0.0)

        if self.current_question_index < len(self.questions) - 1:
            self.next_question()
        else:
            self.show_stats()

    def reset_statistics(self):
        self.correct_answers = []
        self.user_answers = []

    def exit_quiz(self):
        self.session_active = False
        if hasattr(self, 'question_win') and self.question_win:
            self.question_win.destroy()
        messagebox.showinfo("Quiz", "Quiz is exited. Returning to main window.", parent=self.master)

    def show_stats(self):
        if hasattr(self, 'question_win') and self.question_win:
            self.question_win.destroy()

        self.stats_win = tk.Toplevel(self.master)
        self.stats_win.title("Statistics")
        self.center_toplevel(self.stats_win, 600, 400)

        correct_count = sum(1 for score in self.correct_answers if score == 1.0)
        incorrect_count = sum(1 for score in self.correct_answers if score == 0.0)
        skipped_count = sum(1 for answer in self.user_answers if answer is None)
        total_count = len(self.questions)
        total_score = sum(self.correct_answers)
        percentage_correct = (total_score / total_count * 100) if total_count > 0 else 0

        stats_label = tk.Label(
            self.stats_win,
            text=f"You scored {total_score:.2f} out of {total_count} correct!",
            font=("Helvetica", 22)
        )
        stats_label.pack(pady=10)

        tk.Label(self.stats_win, text=f"Correct Answers: {correct_count}", font=("Helvetica", 18)).pack(pady=5)
        tk.Label(self.stats_win, text=f"Incorrect Answers: {incorrect_count}", font=("Helvetica", 18)).pack(pady=5)
        tk.Label(self.stats_win, text=f"Skipped Questions: {skipped_count}", font=("Helvetica", 18)).pack(pady=5)
        tk.Label(self.stats_win, text=f"Score: {percentage_correct:.2f} %", font=("Helvetica", 18)).pack(pady=10)

        nav_frame = tk.Frame(self.stats_win)
        nav_frame.pack(side="bottom", pady=(20, 20))

        review_button = tk.Button(nav_frame, text="Review Answers", font=("Helvetica", 18), command=self.review_answers)
        review_button.pack(side=tk.LEFT, padx=20)

        finish_button = tk.Button(nav_frame, text="Finish", font=("Helvetica", 18), command=self.close_stats_window)
        finish_button.pack(side=tk.LEFT, padx=20)

    def review_answers(self):
        self.stats_win.destroy()
        self.current_question_index = 0
        self.review_window()

    def close_stats_window(self):
        if hasattr(self, 'stats_win') and self.stats_win:
            self.stats_win.destroy()

    # -------------------------------------------------------------------------
    # REVIEW UI (WITH SCROLLING ONLY IF CONTENT > WINDOW) + THICK ARROWS
    #   We keep a dedicated frame for the i-button so that other nav buttons
    #   do NOT shift left/right, but we show/hide the i button as needed.
    # -------------------------------------------------------------------------
    def review_window(self):
        self.review_win = tk.Toplevel(self.master)
        self.review_win.title("Review Answers")
        self.center_toplevel(self.review_win, 1600, 900)

        container = tk.Frame(self.review_win)
        container.pack(fill="both", expand=True)

        self.review_canvas = tk.Canvas(container)
        self.review_canvas.pack(side="left", fill="both", expand=True)

        self.review_scrollbar = tk.Scrollbar(container, orient="vertical", command=self.review_canvas.yview)
        self.review_canvas.configure(yscrollcommand=self.review_scrollbar.set)

        self.review_content_frame = tk.Frame(self.review_canvas)

        if self.current_chapter_data.get("chapter") == "Custom Assessment":
            offset_x = 550
        else:
            offset_x = 400

        self.review_canvas.create_window((offset_x, 0), window=self.review_content_frame, anchor="nw")

        self.review_content_frame.bind("<Configure>", self._configure_review_content)

        self.arrow_up_label = tk.Label(container, text="⬆", font=("Helvetica", 32, "bold"), fg="black")
        self.arrow_down_label = tk.Label(container, text="⬇", font=("Helvetica", 32, "bold"), fg="black")

        self.review_canvas.bind_all("<MouseWheel>", self._on_mousewheel_review)

        bottom_frame = tk.Frame(self.review_win)
        bottom_frame.pack(side="bottom", pady=(30, 30))

        title_text = self.current_session_title if self.current_session_title else "Review Answers"
        self.review_title_label = tk.Label(
            self.review_content_frame,
            text=title_text,
            font=("Helvetica", 24, "bold"),
            justify="center"
        )
        self.review_title_label.pack(pady=10)

        self.question_counter_review = tk.Label(
            self.review_content_frame,
            text=f"Question {self.current_question_index + 1} / {len(self.questions)}",
            font=("Helvetica", 18),
            justify="center"
        )
        self.question_counter_review.pack(pady=10)

        self.review_question_label = tk.Label(
            self.review_content_frame,
            wraplength=900,
            font=("Helvetica", 18),
            justify="center"
        )
        self.review_question_label.pack(pady=10)

        self.options_frame_review = tk.Frame(self.review_content_frame)
        self.options_frame_review.pack(pady=15)

        # Navigation row
        btn_frame = tk.Frame(bottom_frame)
        btn_frame.pack()

        self.previous_review_button = tk.Button(
            btn_frame, text="Previous", font=("Helvetica", 18), command=self.prev_review_question
        )
        self.previous_review_button.pack(side=tk.LEFT, padx=20)

        self.next_review_button = tk.Button(
            btn_frame, text="Next", font=("Helvetica", 18), command=self.next_review_question
        )
        self.next_review_button.pack(side=tk.LEFT, padx=20)

        self.stats_button = tk.Button(
            btn_frame, text="Statistics", font=("Helvetica", 18), command=self.show_stats_from_review
        )
        self.stats_button.pack(side=tk.LEFT, padx=20)

        self.finish_review_button = tk.Button(
            btn_frame, text="Finish", font=("Helvetica", 18), command=self.finish_review
        )
        self.finish_review_button.pack(side=tk.LEFT, padx=20)

        # A dedicated frame for the i button - keeps the layout stable.
        self.info_frame = tk.Frame(btn_frame, width=60, height=40)
        self.info_frame.pack(side=tk.LEFT)

        self.info_button = tk.Button(
            self.info_frame,
            text="     ℹ️",
            font=("Helvetica", 18),
            width=2,
            height=1,  # <-- Maak de knop smaller
            command=self.show_review_info_image
        )
        # We do NOT pack it yet; we will do so in load_review_question if image_i exists.

        self.image_i_shown = False
        self.review_img_i_label = None

        self.load_review_question()

    def _configure_review_content(self, event):
        self.review_canvas.configure(scrollregion=self.review_canvas.bbox("all"))

        content_height = self.review_content_frame.winfo_reqheight()
        canvas_height = self.review_canvas.winfo_height()

        if content_height > canvas_height:
            self.review_scrollbar.pack(side="right", fill="y")
            self.review_canvas.bind_all("<MouseWheel>", self._on_mousewheel_review)
        else:
            self.review_scrollbar.pack_forget()
            self.review_canvas.unbind_all("<MouseWheel>")

        self._update_arrows()

    def _on_mousewheel_review(self, event):
        self.review_canvas.yview_scroll(int(-1*(event.delta / 120)), "units")
        self._update_arrows()

    def _update_arrows(self):
        top_frac, bottom_frac = self.review_canvas.yview()
        container = self.review_canvas.master

        container_width = container.winfo_width()
        container_height = container.winfo_height()

        x_position = container_width - 100
        y_down = container_height - 30
        y_up = y_down - 60

        if top_frac > 0:
            self.arrow_up_label.place(x=x_position, y=y_up, anchor="center")
        else:
            self.arrow_up_label.place_forget()

        if bottom_frac < 1:
            self.arrow_down_label.place(x=x_position, y=y_down, anchor="center")
        else:
            self.arrow_down_label.place_forget()

    def load_review_question(self):
        # Remove any old info image from the previous question
        if hasattr(self, 'review_img_i_label') and self.review_img_i_label:
            self.review_img_i_label.destroy()
            self.review_img_i_label = None
        self.image_i_shown = False

        for widget in self.options_frame_review.winfo_children():
            widget.destroy()

        for child in self.review_content_frame.winfo_children():
            if isinstance(child, tk.Label) and getattr(child, 'image', None) and child != self.review_img_i_label:
                child.destroy()

        self.review_title_label.pack_forget()
        self.question_counter_review.pack_forget()
        self.review_question_label.pack_forget()
        self.options_frame_review.pack_forget()

        self.review_title_label.pack(pady=10)
        self.question_counter_review.pack(pady=10)
        self.review_question_label.pack(pady=10)
        self.options_frame_review.pack(pady=15)

        current_q = self.questions[self.current_question_index]
        self.review_question_label.config(text=current_q["question"])
        self.question_counter_review.config(text=f"Question {self.current_question_index + 1} / {len(self.questions)}")

        image_path = current_q.get("image")
        if image_path:
            if not os.path.isabs(image_path):
                full_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.normpath(image_path))
            else:
                full_image_path = os.path.normpath(image_path)

            if os.path.exists(full_image_path):
                try:
                    img = Image.open(full_image_path)
                    max_width = 800
                    max_height = 600
                    orig_w, orig_h = img.size
                    scale_factor = min(max_width / orig_w, max_height / orig_h)

                    if scale_factor < 1:
                        new_w = int(orig_w * scale_factor)
                        new_h = int(orig_h * scale_factor)
                        img = img.resize((new_w, new_h), Image.LANCZOS)

                    self.review_img = ImageTk.PhotoImage(img)
                    self.review_img_label = tk.Label(self.review_content_frame, image=self.review_img)
                    self.review_img_label.image = self.review_img
                    self.review_img_label.pack(before=self.options_frame_review, pady=10)
                except Exception as e:
                    print(f"Could not load/resize image: {e}")

        # Hide or show the i button depending on the presence of image_i
        if "image_i" in current_q:
            # If there's image_i, pack the button so it's visible
            self.info_button.pack(side="left")
        else:
            # If no image_i, hide the i button
            self.info_button.pack_forget()

        correct_answers = current_q["answer"]
        user_selected = self.user_answers[self.current_question_index] if self.user_answers[self.current_question_index] is not None else []

        if isinstance(correct_answers, list):
            correct_answers_set = set(correct_answers)
        else:
            correct_answers_set = {correct_answers}

        options = self.shuffled_options[self.current_question_index]

        for idx, option in enumerate(options):
            explanation = current_q.get("explanation", {}).get(option, "No explanation available.")
            text_line = f"{option}: {explanation}"

            user_selected_this = (idx in user_selected)
            is_correct_this = (option in correct_answers_set)

            if user_selected_this and is_correct_this:
                label = tk.Label(
                    self.options_frame_review,
                    text=f"[Correct ✓] {option}",
                    fg="green",
                    font=("Helvetica", 18, "bold")
                )
                exp_label = tk.Label(
                    self.options_frame_review,
                    text=text_line,
                    fg="black",
                    font=("Helvetica", 16),
                    wraplength=900,
                    justify="left"
                )
            elif user_selected_this and not is_correct_this:
                label = tk.Label(
                    self.options_frame_review,
                    text=f"[Incorrect X] {option}",
                    fg="red",
                    font=("Helvetica", 18, "bold")
                )
                exp_label = tk.Label(
                    self.options_frame_review,
                    text=text_line,
                    fg="black",
                    font=("Helvetica", 16),
                    wraplength=900,
                    justify="left"
                )
            elif not user_selected_this and is_correct_this:
                label = tk.Label(
                    self.options_frame_review,
                    text=f"{option}",
                    fg="green",
                    font=("Helvetica", 18)
                )
                exp_label = tk.Label(
                    self.options_frame_review,
                    text=text_line,
                    fg="black",
                    font=("Helvetica", 16),
                    wraplength=900,
                    justify="left"
                )
            else:
                label = tk.Label(
                    self.options_frame_review,
                    text=f"{option}",
                    fg="red",
                    font=("Helvetica", 18)
                )
                exp_label = tk.Label(
                    self.options_frame_review,
                    text=text_line,
                    fg="black",
                    font=("Helvetica", 16),
                    wraplength=900,
                    justify="left"
                )

            label.pack(anchor="w", pady=(10, 0))
            exp_label.pack(anchor="w", pady=(0, 10))

    def prev_review_question(self):
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.load_review_question()
            self._update_arrows()

    def next_review_question(self):
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.load_review_question()
            self._update_arrows()
        else:
            self.show_stats_from_review()

    def show_stats_from_review(self):
        self.review_win.destroy()
        self.show_stats()

    def finish_review(self):
        self.review_win.destroy()
        self.session_active = False

    def show_review_info_image(self):
        """
        If user clicks ℹ️, toggle showing/hiding the 'image_i'.
        """
        current_q = self.questions[self.current_question_index]
        image_i_path = current_q.get("image_i")
        if not image_i_path:
            return  # No image_i to show, do nothing

        # If we have it already displayed, remove it (toggle off)
        if self.image_i_shown and self.review_img_i_label:
            self.review_img_i_label.destroy()
            self.review_img_i_label = None
            self.image_i_shown = False
            return

        # Otherwise, show it
        if getattr(sys, 'frozen', False):
            current_directory = os.path.dirname(sys.executable)
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))

        full_path = os.path.join(current_directory, os.path.normpath(image_i_path))
        if not os.path.exists(full_path):
            messagebox.showerror("Error", f"image_i not found at: {full_path}", parent=self.review_win)
            return

        try:
            pil_img = Image.open(full_path)
            max_width, max_height = 800, 600
            w, h = pil_img.size
            scale = min(max_width / w, max_height / h)
            if scale < 1:
                pil_img = pil_img.resize((int(w*scale), int(h*scale)), Image.LANCZOS)

            self.info_images[image_i_path] = ImageTk.PhotoImage(pil_img)
            self.review_img_i_label = tk.Label(self.review_content_frame, image=self.info_images[image_i_path])
            self.review_img_i_label.image = self.info_images[image_i_path]
            self.review_img_i_label.pack(before=self.options_frame_review, pady=10)
            self.image_i_shown = True

        except Exception as e:
            messagebox.showerror("Error", f"Could not load image_i: {e}", parent=self.review_win)

    def close_question_window(self):
        if hasattr(self, 'question_win') and self.question_win:
            self.question_win.destroy()

    # -------------------------------------------------------------------------
    # Add/Edit Questions in addedQuestions.json
    # -------------------------------------------------------------------------
    def open_add_question_window(self, is_edit=False, question_win=None, question_number=None):
        self.temp_image_source = None  # Original path from file dialog
        self.temp_image_target = None  # Path in linux_questions_images
        self.renamed_filename = None

        self.question_win = tk.Toplevel(self.master)
        self.question_win.geometry("1600x900")
        self.center_toplevel(self.question_win, 1600, 900)

        window_title = "Add New Question" if not is_edit else "Edit Question"
        self.question_win.title(window_title)

        title_label = tk.Label(self.question_win, text=window_title, font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(20, 10))

        tk.Label(self.question_win, text="Question:", font=("Helvetica", 12)).pack(pady=(10, 5), padx=(50, 0))

        self.question_text = tk.Text(self.question_win, width=83, height=3, font=("Helvetica", 12))
        self.question_text.pack(pady=(10, 30))
        self.question_text.pack(padx=(65, 0))

        self.options_vars = []
        self.explanations_vars = []
        frame = tk.Frame(self.question_win)
        frame.pack(pady=5)

        for i in range(5):
            tk.Label(frame, text=f"Option {i + 1}:", font=("Helvetica", 10)).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            opt_text = tk.Text(frame, width=35, height=3, font=("Helvetica", 12))
            opt_text.grid(row=i, column=1, padx=5, pady=5)
            self.options_vars.append(opt_text)

            tk.Label(frame, text=f"Explanation {i + 1}:", font=("Helvetica", 10)).grid(row=i, column=2, padx=5, pady=5, sticky='e')
            exp_text = tk.Text(frame, width=35, height=3, font=("Helvetica", 12))
            exp_text.grid(row=i, column=3, padx=5, pady=5)
            self.explanations_vars.append(exp_text)

        self.correct_answers = []

        correct_answer_frame = tk.Frame(self.question_win)
        correct_answer_frame.pack(pady=(30, 5))

        tk.Label(correct_answer_frame, text="Correct Answer:", font=("Helvetica", 12)).pack(side="left", padx=5)
        self.correct_answer_var = tk.StringVar(value="Select answer")
        self.correct_answer_menu = tk.OptionMenu(
            correct_answer_frame,
            self.correct_answer_var,
            *[f"Option {i + 1}" for i in range(5)],
            command=self.add_correct_answer
        )
        self.correct_answer_menu.pack(side="left", padx=5)

        selected_answers_frame = tk.Frame(self.question_win)
        selected_answers_frame.pack(pady=(5, 30))

        self.correct_answers_display = tk.Label(selected_answers_frame, text="Selected Answers: []", font=("Helvetica", 12))
        self.correct_answers_display.pack(side="left")

        self.remove_last_answer_btn = tk.Button(selected_answers_frame, text="❌", command=self.remove_last_correct_answer, height=2)
        self.remove_last_answer_btn.pack(side="left", padx=5)

        def select_image_and_keep_on_top():
            self.select_image_for_later_copy()
            self.question_win.lift()

        tk.Button(self.question_win, text="Select Image", command=select_image_and_keep_on_top, height=2).pack(pady=(5, 5))
        self.image_path = tk.StringVar()

        image_path_frame = tk.Frame(self.question_win)
        image_path_frame.pack(pady=(0, 5))

        self.image_path_entry = tk.Entry(image_path_frame, textvariable=self.image_path, width=60)
        self.image_path_entry.pack(side="left", padx=5, ipady=5)

        self.clear_image_btn = tk.Button(image_path_frame, text="❌", command=self.clear_image_path, height=2)
        self.clear_image_btn.pack(side="left", padx=5)

        bottom_frame = tk.Frame(self.question_win)
        bottom_frame.pack(pady=(30, 50), ipady=8)

        if not is_edit:
            self.add_button = tk.Button(
                bottom_frame,
                text="Add Question",
                command=self.save_question_to_json,
                width=20,
                height=2
            )
            self.add_button.pack(side="left", padx=10)
        else:
            self.add_button = tk.Button(
                bottom_frame,
                text="Save Changes",
                command=lambda: self.save_edited_question(question_number),
                width=20,
                height=2
            )
            self.add_button.pack(side="left", padx=10)

        def close_window():
            self.question_win.destroy()
            if is_edit and hasattr(self, 'edit_question_win') and self.edit_question_win:
                self.edit_question_win.lift()

        close_btn = tk.Button(
            bottom_frame,
            text="Close",
            width=20,
            height=2,
            command=close_window
        )
        close_btn.pack(side="left", padx=10)

    def select_image_for_later_copy(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.gif;*.tiff")]
        )
        if not file_path:
            return

        rename = messagebox.askyesno("Rename", "Would you like to rename the image?", parent=self.question_win)
        if rename:
            new_name = simpledialog.askstring("Rename file", "Enter new filename (without extension):", parent=self.question_win)
        else:
            new_name = None

        if getattr(sys, 'frozen', False):
            current_directory = os.path.dirname(sys.executable)
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))

        images_folder = os.path.join(current_directory, 'assets', 'linux_questions_images')
        os.makedirs(images_folder, exist_ok=True)

        base_name = os.path.splitext(os.path.basename(file_path))[0]

        if new_name:
            final_filename = new_name
        else:
            final_filename = base_name

        if not final_filename.lower().endswith(('.jpg', '.jpeg')):
            final_filename += ".jpg"

        self.temp_image_source = file_path
        final_path = os.path.join(images_folder, final_filename)
        self.temp_image_target = final_path

        self.image_path.set(os.path.relpath(final_path, current_directory))

    def copy_and_convert_image_later(self):
        if not self.temp_image_source or not self.temp_image_target:
            return

        try:
            with Image.open(self.temp_image_source) as im:
                im = im.convert("RGB")
                im.save(self.temp_image_target, "JPEG")
        except Exception as e:
            self.show_error_message(f"Could not copy/convert image: {e}")

    def clear_image_path(self):
        self.image_path.set("")
        self.temp_image_source = None
        self.temp_image_target = None
        self.renamed_filename = None

    def add_correct_answer(self, selected_option):
        option_index = int(selected_option.split()[-1]) - 1
        option_text = self.options_vars[option_index].get("1.0", tk.END).strip()
        if not option_text:
            self.show_error_message(
                f"Option {option_index + 1} is empty. Please fill it in before selecting it as a correct answer."
            )
            return

        if option_text not in self.correct_answers:
            self.correct_answers.append(option_text)
            self.correct_answers_display.config(text=f"Selected Answers: {self.correct_answers}")

    def remove_last_correct_answer(self):
        if self.correct_answers:
            self.correct_answers.pop()
            self.correct_answers_display.config(text=f"Selected Answers: {self.correct_answers}")

    def reset_add_question_fields(self):
        self.question_text.delete("1.0", tk.END)
        for text_widget in self.options_vars:
            text_widget.delete("1.0", tk.END)
        for text_widget in self.explanations_vars:
            text_widget.delete("1.0", tk.END)
        self.correct_answers.clear()
        self.correct_answers_display.config(text="Selected Answers: []")
        self.image_path.set("")
        self.correct_answer_var.set("Select answer")
        self.temp_image_source = None
        self.temp_image_target = None

    def save_question_to_json(self):
        question = self.question_text.get("1.0", tk.END).strip()
        options = [text.get("1.0", tk.END).strip() for text in self.options_vars if text.get("1.0", tk.END).strip()]
        explanations = {options[i]: self.explanations_vars[i].get("1.0", tk.END).strip() for i in range(len(options))}

        if not question or not options or not self.correct_answers:
            self.show_error_message("Please fill in all fields and select at least one correct answer.")
            return

        if getattr(sys, 'frozen', False):
            current_directory = os.path.dirname(sys.executable)
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))

        file_path = os.path.join(current_directory, 'assets', 'linux_questions', 'addedQuestions.json')

        if self.temp_image_source and self.temp_image_target:
            self.copy_and_convert_image_later()
            final_relative_path = os.path.relpath(self.temp_image_target, current_directory)
        else:
            final_relative_path = ""

        new_question = {
            "number": 0,  # Will be replaced below
            "question": question,
            "options": options,
            "answer": self.correct_answers,
            "explanation": explanations
        }

        if final_relative_path:
            new_question["image"] = final_relative_path

        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {"chapters": [{"description": "Added Questions", "questions": []}]}
            else:
                data = {"chapters": [{"description": "Added Questions", "questions": []}]}

            questions_in_file = data['chapters'][0]['questions']
            if questions_in_file:
                max_number = max(q['number'] for q in questions_in_file)
            else:
                max_number = 0

            new_question['number'] = max_number + 1

            questions_in_file.append(new_question)

            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

            messagebox.showinfo("Success", "Question added successfully!", parent=self.question_win)
            self.question_win.lift()
            self.reset_add_question_fields()

        except Exception as e:
            self.show_error_message(f"Failed to save question: {e}")

    def open_edit_question_window(self):
        self.edit_question_win = tk.Toplevel(self.master)
        self.edit_question_win.title("Edit Question")
        self.center_toplevel(self.edit_question_win, 800, 600)

        listbox_frame = tk.Frame(self.edit_question_win)
        listbox_frame.pack(pady=10)

        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        self.question_listbox = tk.Listbox(
            listbox_frame,
            font=("Helvetica", 12),
            width=80,
            height=15,
            yscrollcommand=scrollbar.set,
            selectmode=tk.MULTIPLE,
            exportselection=False
        )
        self.question_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.question_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.question_listbox.bind("<Button-1>", self.toggle_question_selection, add="+")

        self.load_questions_for_editing()

        button_frame = tk.Frame(self.edit_question_win)
        button_frame.pack(pady=20)

        button_font = ("Helvetica", 14, "bold")

        self.view_button = tk.Button(button_frame, text="👁️ View", font=button_font, command=self.view_question)
        self.view_button.configure(state="disabled", fg="gray")
        self.view_button.pack(side=tk.LEFT, padx=10)

        self.edit_button = tk.Button(button_frame, text="✏️ Edit", font=button_font, command=self.edit_question)
        self.edit_button.configure(state="disabled", fg="gray")
        self.edit_button.pack(side=tk.LEFT, padx=10)

        self.new_question_button = tk.Button(
            button_frame,
            text="Add New Question",
            font=button_font,
            command=self.open_add_question_window
        )
        self.new_question_button.configure(state="normal", fg="black")
        self.new_question_button.pack(side=tk.LEFT, padx=10)

        self.delete_button = tk.Button(button_frame, text="🗑️ Delete", font=button_font, command=self.delete_question)
        self.delete_button.configure(state="disabled", fg="gray")
        self.delete_button.pack(side=tk.LEFT, padx=10)

        self.close_button = tk.Button(button_frame, text="Close", font=button_font, command=self.edit_question_win.destroy)
        self.close_button.pack(side=tk.LEFT, padx=10)

    def toggle_question_selection(self, event):
        lb = event.widget
        index = lb.nearest(event.y)
        if index < 0:
            return

        current_selection = lb.curselection()
        if index in current_selection:
            lb.selection_clear(index)
        else:
            lb.selection_set(index)

        self.on_question_listbox_select()
        return "break"

    def on_question_listbox_select(self):
        sel = self.question_listbox.curselection()
        if len(sel) == 1:
            self.view_button.configure(state="normal", fg="black")
            self.edit_button.configure(state="normal", fg="black")
        else:
            self.view_button.configure(state="disabled", fg="gray")
            self.edit_button.configure(state="disabled", fg="gray")

        if len(sel) >= 1:
            self.delete_button.configure(state="normal", fg="black")
        else:
            self.delete_button.configure(state="disabled", fg="gray")

    def load_questions_for_editing(self):
        if getattr(sys, 'frozen', False):
            current_directory = os.path.dirname(sys.executable)
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))

        file_path = os.path.join(current_directory, 'assets', 'linux_questions', 'addedQuestions.json')

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                questions = data['chapters'][0]['questions']
                for question in questions:
                    display_text = f"Nr. {question['number']}: {question['question']}"
                    self.question_listbox.insert(tk.END, display_text)
        except Exception as e:
            self.show_error_message(f"Could not load questions for editing: {e}")

    def view_question(self):
        sel = self.question_listbox.curselection()
        if len(sel) != 1:
            return
        question_index_in_list = sel[0]

        if getattr(sys, 'frozen', False):
            current_directory = os.path.dirname(sys.executable)
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))

        file_path = os.path.join(current_directory, 'assets', 'linux_questions', 'addedQuestions.json')

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                question = data['chapters'][0]['questions'][question_index_in_list]

                view_win = tk.Toplevel(self.master)
                view_win.title("View Question")
                self.center_toplevel(view_win, 600, 800)

                question_label = tk.Label(view_win, text=question["question"], wraplength=550, font=("Helvetica", 16))
                question_label.pack(pady=(20, 10))

                options_frame = tk.Frame(view_win)
                options_frame.pack(pady=10)

                correct_answers = question["answer"] if isinstance(question["answer"], list) else [question["answer"]]
                for option in question["options"]:
                    answer_label = tk.Label(options_frame, text=f"{option}", font=("Helvetica", 14, "bold"))
                    answer_label.pack(anchor="w", pady=(10, 0))
                    explanation = question["explanation"].get(option, "No explanation available.")
                    explanation_label = tk.Label(options_frame, text=f"   {explanation}", font=("Helvetica", 12))
                    explanation_label.pack(anchor="w", pady=(0, 20))

                correct_answer_label = tk.Label(
                    view_win,
                    text=f"Correct Answer(s): {', '.join(correct_answers)}",
                    font=("Helvetica", 14)
                )
                correct_answer_label.pack(pady=(10, 10))

                if "image" in question and question["image"]:
                    image_path = question["image"]
                    if not os.path.isabs(image_path):
                        full_image_path = os.path.join(current_directory, os.path.normpath(image_path))
                    else:
                        full_image_path = os.path.normpath(image_path)

                    if os.path.exists(full_image_path):
                        img = Image.open(full_image_path)
                        img = img.resize((300, 150), Image.LANCZOS)
                        question_image = ImageTk.PhotoImage(img)
                        image_label = tk.Label(view_win, image=question_image)
                        image_label.image = question_image
                        image_label.pack(pady=(10, 20))

                button_frame = tk.Frame(view_win)
                button_frame.pack(pady=20)

                edit_button = tk.Button(
                    button_frame,
                    text="✏️ Edit",
                    font=("Helvetica", 14),
                    command=lambda: self.edit_question_in_view(view_win, question_index_in_list)
                )
                edit_button.pack(side=tk.LEFT, padx=10)

                delete_button = tk.Button(
                    button_frame,
                    text="🗑️ Delete",
                    font=("Helvetica", 14),
                    command=lambda: self.delete_question_in_view(view_win, question_index_in_list)
                )
                delete_button.pack(side=tk.LEFT, padx=10)

                close_button = tk.Button(button_frame, text="Close", font=("Helvetica", 14), command=view_win.destroy)
                close_button.pack(side=tk.LEFT, padx=10)

        except Exception as e:
            self.show_error_message(f"Could not load question: {e}")

    def edit_question_in_view(self, view_win, question_index_in_list):
        view_win.destroy()
        self.edit_question_win.lift()
        self.edit_question_specific_index(question_index_in_list)

    def delete_question_in_view(self, view_win, question_index_in_list):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this question?",
                               parent=view_win):
            view_win.destroy()
            self.edit_question_win.lift()
            self.delete_question_final(question_index_in_list)
        else:
            view_win.lift()
            self.center_toplevel(view_win, 600, 800)

    def edit_question(self):
        sel = self.question_listbox.curselection()
        if len(sel) != 1:
            return
        question_index_in_list = sel[0]
        self.edit_question_specific_index(question_index_in_list)

    def edit_question_specific_index(self, question_index_in_list):
        if getattr(sys, 'frozen', False):
            current_directory = os.path.dirname(sys.executable)
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))

        file_path = os.path.join(current_directory, 'assets', 'linux_questions', 'addedQuestions.json')

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                question = data['chapters'][0]['questions'][question_index_in_list]

                actual_question_number = question['number']

                self.open_add_question_window(is_edit=True, question_win=self.edit_question_win, question_number=actual_question_number)
                self.question_text.insert(tk.END, question["question"])

                for i, option in enumerate(question["options"]):
                    self.options_vars[i].delete("1.0", tk.END)
                    self.options_vars[i].insert(tk.END, option)

                for i, option_text in enumerate(question["options"]):
                    exp = question["explanation"].get(option_text, "")
                    self.explanations_vars[i].delete("1.0", tk.END)
                    self.explanations_vars[i].insert(tk.END, exp)

                if isinstance(question["answer"], list):
                    self.correct_answers = question["answer"]
                else:
                    self.correct_answers = [question["answer"]]
                self.correct_answers_display.config(text=f"Selected Answers: {self.correct_answers}")

                if "image" in question and question["image"]:
                    self.image_path.set(question["image"])
                    self.temp_image_source = None
                    self.temp_image_target = None

                self.add_button.config(
                    text="Save Changes",
                    command=lambda: self.save_edited_question(actual_question_number)
                )

        except Exception as e:
            self.show_error_message(f"Could not load question for editing: {e}")

    def delete_question(self):
        sel = self.question_listbox.curselection()
        if not sel:
            self.show_error_message("Please select at least one question to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected question(s)?",
                               parent=self.edit_question_win):
            for index in reversed(sel):
                self.delete_question_final(index)
            self.edit_question_win.lift()

    def delete_question_final(self, question_index_in_list):
        if getattr(sys, 'frozen', False):
            current_directory = os.path.dirname(sys.executable)
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))

        file_path = os.path.join(current_directory, 'assets', 'linux_questions', 'addedQuestions.json')

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            questions_list = data['chapters'][0]['questions']

            if question_index_in_list < len(questions_list):
                del questions_list[question_index_in_list]

                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)

                self.question_listbox.delete(question_index_in_list)
            self.on_question_listbox_select()

        except Exception as e:
            self.show_error_message(f"Could not delete question: {e}")

    def save_edited_question(self, question_number):
        question = self.question_text.get("1.0", tk.END).strip()
        options = [text.get("1.0", tk.END).strip() for text in self.options_vars if text.get("1.0", tk.END).strip()]

        explanations = {}
        for i in range(len(options)):
            opt = options[i]
            exp = self.explanations_vars[i].get("1.0", tk.END).strip()
            explanations[opt] = exp

        if not question or not options or not self.correct_answers:
            self.show_error_message("Please fill in all fields and select at least one correct answer.")
            return

        if getattr(sys, 'frozen', False):
            current_directory = os.path.dirname(sys.executable)
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))

        file_path = os.path.join(current_directory, 'assets', 'linux_questions', 'addedQuestions.json')

        final_relative_path = self.image_path.get().strip()

        if self.temp_image_source and self.temp_image_target:
            self.copy_and_convert_image_later()
            final_relative_path = os.path.relpath(self.temp_image_target, current_directory)

        new_question = {
            "number": question_number,
            "question": question,
            "options": options,
            "answer": self.correct_answers,
            "explanation": explanations
        }

        if final_relative_path:
            new_question["image"] = final_relative_path

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            questions_list = data['chapters'][0]['questions']
            index_in_file = None
            for idx, q in enumerate(questions_list):
                if q['number'] == question_number:
                    index_in_file = idx
                    break

            if index_in_file is None:
                self.show_error_message("Could not find the original question in JSON. Aborting edit.")
                return

            data['chapters'][0]['questions'][index_in_file] = new_question

            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

            messagebox.showinfo("Success", "Question updated successfully!", parent=self.question_win)
            self.reset_add_question_fields()
            self.question_win.destroy()
            self.edit_question_win.lift()

        except Exception as e:
            self.show_error_message(f"Failed to save question: {e}")

    # -------------------------------------------------------------------------
    # General error popup
    # -------------------------------------------------------------------------
    def show_error_message(self, message):
        if hasattr(self, 'question_win') and self.question_win and self.question_win.winfo_exists():
            parent_window = self.question_win
        elif hasattr(self, 'edit_assessment_details_win') and self.edit_assessment_details_win and self.edit_assessment_details_win.winfo_exists():
            parent_window = self.edit_assessment_details_win
        elif hasattr(self, 'assessment_win') and self.assessment_win and self.assessment_win.winfo_exists():
            parent_window = self.assessment_win
        elif hasattr(self, 'edit_question_win') and self.edit_question_win and self.edit_question_win.winfo_exists():
            parent_window = self.edit_question_win
        else:
            parent_window = self.master

        messagebox.showerror("Error", message, parent=parent_window)
        parent_window.lift()


# ------------------------------------------------------------------------------
# Main application entry point
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()



    



#oelie Lekker
# branch main





