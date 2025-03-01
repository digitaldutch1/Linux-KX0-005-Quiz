


import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import random
import webbrowser
import os
import sys

def load_questions_from_json(filename):
    try:
        if getattr(sys, 'frozen', False):
            current_directory = sys._MEIPASS
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
    try:
        if getattr(sys, 'frozen', False):
            current_directory = sys._MEIPASS
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))
        
        full_path = os.path.join(current_directory, 'assets', 'linux_questions', filename)

        with open(full_path, 'r') as file:
            data = json.load(file)
            return len(data['chapters'][0]['questions'])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        messagebox.showerror("Error", f"Could not load questions: {e}")
        return 0

class QuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Linux+ KX0-005")
        self.master.geometry("1200x800")
        self.current_chapter_data = None
        self.current_question_index = 0
        self.correct_answers = []
        self.user_answers = []
        self.session_active = False
        self.assessment_mode = False
        self.current_question = None  # Initialize current_question
        self.current_session_title = ""  # Voeg dit toe om de huidige sessietitel op te slaan

        self.assessments = self.load_assessments()

        self.center_window()

        self.banner = tk.Label(self.master, text="Linux+ KX0-005", font=("Helvetica", 40, "bold"))
        self.banner.pack(pady=20)

        self.navbar_frame = tk.Frame(self.master)
        self.navbar_frame.pack()

        self.ebook_menu = tk.Menubutton(self.navbar_frame, text="Ebook", font=("Helvetica", 26), relief="raised", borderwidth=1)
        self.ebook_menu.menu = tk.Menu(self.ebook_menu, tearoff=0, font=("Helvetica", 18))
        self.ebook_menu["menu"] = self.ebook_menu.menu
        self.ebook_menu.pack(side="left", padx=20)

        # Menu Ebook
        self.ebook_menu.menu.add_command(label="Linux +", command=self.open_ebook)
        self.ebook_menu.menu.add_command(label="Orchestration tools", command=self.open_orchestration_tools)
        self.ebook_menu.menu.add_command(label="Git & Github", command=self.open_git_github)
        self.ebook_menu.menu.add_command(label="Summary Chapter 2: Introduction to Services", command=self.open_summary_chapter_2)
        self.ebook_menu.menu.add_command(label="Summary Chapter 3: Managing Files, Directories, and Tekst", command=self.open_summary_chapter_3)
        self.ebook_menu.menu.add_command(label="Summary Chapter 4: Searching and Analyzing tekst", command=self.open_summary_chapter_4)
        self.ebook_menu.menu.add_command(label="Summary Chapter 5: Explaining the Boot Process", command=self.open_summary_chapter_5)

        self.chapter_menu = tk.Menubutton(self.navbar_frame, text="Chapters", font=("Helvetica", 26), relief="raised", borderwidth=1)
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

        # Add the new "Exercise" menu
        self.exercise_menu = tk.Menubutton(self.navbar_frame, text="Exercise", font=("Helvetica", 26), relief="raised", borderwidth=1)
        self.exercise_menu.menu = tk.Menu(self.exercise_menu, tearoff=0, font=("Helvetica", 18))
        self.exercise_menu["menu"] = self.exercise_menu.menu
        self.exercise_menu.pack(side="left", padx=20)

        # Add exercises to the "Exercise" menu
        # Use the standalone function directly
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

        self.assessment_menu = tk.Menubutton(self.navbar_frame, text="Assessment", font=("Helvetica", 26), relief="raised", borderwidth=1)
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

        # Voeg dynamisch gemaakte assessments toe aan het menu
        self.update_assessment_menu()

        self.edit_assessment_menu = tk.Menubutton(self.navbar_frame, text="Edit Assessment", font=("Helvetica", 26), relief="raised", borderwidth=1)
        self.edit_assessment_menu.menu = tk.Menu(self.edit_assessment_menu, tearoff=0, font=("Helvetica", 18))
        self.edit_assessment_menu["menu"] = self.edit_assessment_menu.menu
        self.edit_assessment_menu.pack(side="left", padx=20)

        self.edit_assessment_menu.menu.add_command(label="Add Assessment", command=self.make_assessment)

        self.update_create_assessment_menu()

        self.add_question_menu = tk.Menubutton(self.navbar_frame, text="Add Questions", font=("Helvetica", 26), relief="raised", borderwidth=1)
        self.add_question_menu.menu = tk.Menu(self.add_question_menu, tearoff=0, font=("Helvetica", 18))
        self.add_question_menu["menu"] = self.add_question_menu.menu
        self.add_question_menu.pack(side="left", padx=20)

        self.add_question_menu.menu.add_command(label="Add Question", command=self.make_question)
        self.add_question_menu.menu.add_command(label="List Questions", command=self.list_questions)

        # Voeg afbeelding toe onder de navigatiebalk met dynamisch pad
        self.add_image()

    def add_image(self):
        try:
            if getattr(sys, 'frozen', False):
                current_directory = sys._MEIPASS
            else:
                current_directory = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(current_directory, 'assets', 'icon', 'linux afbeelding 2.png')

            self.image = tk.PhotoImage(file=image_path)
            self.image_label = tk.Label(self.master, image=self.image)
            self.image_label.pack(pady=(50, 20))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {e}")

    # functie open pdf
    def open_ebook(self):
        if getattr(sys, 'frozen', False):
            current_directory = sys._MEIPASS
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(current_directory, 'assets', 'linuxbook', 'linuxbook.pdf')

        if os.path.exists(pdf_path):
            webbrowser.open(pdf_path)
        else:
            messagebox.showerror("Error", "Ebook niet gevonden.")

    def open_orchestration_tools(self):
        if getattr(sys, 'frozen', False):
            current_directory = sys._MEIPASS
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(current_directory, 'assets', 'linuxbook', 'Orchestration tools.pdf')

        if os.path.exists(pdf_path):
            webbrowser.open(pdf_path)
        else:
            messagebox.showerror("Error", "Chapter 2 PDF niet gevonden.")

    def open_git_github(self):
        if getattr(sys, 'frozen', False):
            current_directory = sys._MEIPASS
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(current_directory, 'assets', 'linuxbook', 'Git & Github.pdf')

        if os.path.exists(pdf_path):
            webbrowser.open(pdf_path)
        else:
            messagebox.showerror("Error", "Chapter 2 PDF niet gevonden.")
    
    def open_summary_chapter_2(self):
        if getattr(sys, 'frozen', False):
            current_directory = sys._MEIPASS
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(current_directory, 'assets', 'linuxbook', 'Chapter 2 introduction to services.pdf')

        if os.path.exists(pdf_path):
            webbrowser.open(pdf_path)
        else:
            messagebox.showerror("Error", "Chapter 2 PDF niet gevonden.")

    def open_summary_chapter_3(self):
        if getattr(sys, 'frozen', False):
            current_directory = sys._MEIPASS
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(current_directory, 'assets', 'linuxbook', 'Chapter 3 Managing Files, Directories, and Tekst.pdf')

        if os.path.exists(pdf_path):
            webbrowser.open(pdf_path)
        else:
            messagebox.showerror("Error", "Chapter 3 PDF niet gevonden.")

    def open_summary_chapter_4(self):
        if getattr(sys, 'frozen', False):
            current_directory = sys._MEIPASS
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(current_directory, 'assets', 'linuxbook', 'Chapter 4 Searching and Analyzing tekst.pdf')

        if os.path.exists(pdf_path):
            webbrowser.open(pdf_path)
        else:
            messagebox.showerror("Error", "Chapter 4 PDF niet gevonden.")

    def open_summary_chapter_5(self):
        if getattr(sys, 'frozen', False):
            current_directory = sys._MEIPASS
        else:
            current_directory = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(current_directory, 'assets', 'linuxbook', 'Chapter 5 Explaining the Boot Process.pdf')

        if os.path.exists(pdf_path):
            webbrowser.open(pdf_path)
        else:
            messagebox.showerror("Error", "Chapter 4 PDF niet gevonden.")

    def make_assessment(self):
        self.assessment_win = tk.Toplevel(self.master)
        self.assessment_win.title("Create New Assessment")
        self.assessment_win.geometry("600x400")

        self.assessment_win.grid_rowconfigure(1, weight=1)
        self.assessment_win.grid_columnconfigure(0, weight=1)
        self.assessment_win.grid_columnconfigure(1, weight=1)

        content_frame = tk.Frame(self.assessment_win)
        content_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

        tk.Label(content_frame, text="Title:", font=("Helvetica", 14)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.title_entry = tk.Entry(content_frame, width=50)
        self.title_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(content_frame, text="Description:", font=("Helvetica", 14)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.description_entry = tk.Text(content_frame, height=5, width=50)
        self.description_entry.grid(row=1, column=1, padx=10, pady=10)

        self.question_frame = tk.Frame(content_frame, borderwidth=1, relief="solid")
        self.question_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.question_frame.grid_rowconfigure(0, weight=1)
        self.question_frame.grid_columnconfigure(0, weight=1)

        tk.Label(self.question_frame, text="Add Questions", font=("Helvetica", 12)).pack(pady=(5, 0))
        
        self.add_question_buttons_frame = tk.Frame(self.question_frame)
        self.add_question_buttons_frame.pack(pady=10)

        self.create_question_btn = tk.Button(self.add_question_buttons_frame, text="Add Question", command=self.make_question)
        self.create_question_btn.pack(side="left", padx=10)

        self.list_questions_btn = tk.Button(self.add_question_buttons_frame, text="List Questions", command=self.list_questions)
        self.list_questions_btn.pack(side="left", padx=10)

        self.question_count_label = tk.Label(self.question_frame, text="Questions: 0", font=("Helvetica", 12))
        self.question_count_label.pack(pady=5)

        self.create_assessment_btn = tk.Button(content_frame, text="Create", command=self.save_assessment)
        self.create_assessment_btn.grid(row=3, column=0, columnspan=2, pady=10)

        self.current_question_count = 0

    def save_assessment(self):
        title = self.title_entry.get().strip()
        description = self.description_entry.get("1.0", tk.END).strip()

        if any(assessment['title'] == title for assessment in self.assessments):
            messagebox.showerror("Error", "Title already exists. Please choose a different title.")
            return

        if not title or not description:
            messagebox.showerror("Error", "Title and Description cannot be empty.")
            return

        assessment_data = {
            "title": title,
            "description": description,
            "questions_count": self.current_question_count
        }

        self.assessments.append(assessment_data)
        self.update_assessment_json()
        self.update_assessment_menu()
        self.update_create_assessment_menu()
        self.assessment_win.destroy()

    def update_assessment_json(self):
        try:
            if getattr(sys, 'frozen', False):
                current_directory = os.path.dirname(sys.executable)
            else:
                current_directory = os.path.dirname(os.path.abspath(__file__))

            full_path = os.path.join(current_directory, 'assets', 'linux_questions', 'addedAssessments.json')

            print(f"Saving assessments to: {full_path}")
            
            with open(full_path, 'w') as file:
                json.dump(self.assessments, file, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save assessments: {e}")

    def load_assessments(self):
        try:
            if getattr(sys, 'frozen', False):
                current_directory = os.path.dirname(sys.executable)
            else:
                current_directory = os.path.dirname(os.path.abspath(__file__))
            
            full_path = os.path.join(current_directory, 'assets', 'linux_questions', 'addedAssessments.json')

            print(f"Loading assessments from: {full_path}")
            
            if not os.path.exists(full_path):
                print(f"File not found. Creating a new one at: {full_path}")
                with open(full_path, 'w') as file:
                    json.dump([], file)

            with open(full_path, 'r') as file:
                data = json.load(file)
                return data
        except Exception as e:
            print(f"Error loading assessments: {e}")
            return []

    def update_assessment_menu(self):
        static_items_end_index = 3
        end_index = self.assessment_menu.menu.index('end')
        if end_index is not None:
            for index in range(static_items_end_index, end_index + 1):
                self.assessment_menu.menu.delete(static_items_end_index)

        for assessment in self.assessments:
            title = assessment["title"]
            questions_count = assessment["questions_count"]
            self.assessment_menu.menu.add_command(
                label=f"{title} ({questions_count})",
                command=lambda title=title: self.start_assessment_custom(title)
            )


    def update_create_assessment_menu(self):
        while self.edit_assessment_menu.menu.index('end') > 0:
            self.edit_assessment_menu.menu.delete(1)

        for assessment in self.assessments:
            title = assessment["title"]
            self.edit_assessment_menu.menu.add_command(
                label=title,
                command=lambda title=title: self.edit_assessment(title)
            )

    def start_assessment_custom(self, title):
        messagebox.showinfo("Start Assessment", f"Starting assessment: {title}")

    def edit_assessment(self, title):
        messagebox.showinfo("Edit Assessment", f"Editing assessment: {title}")

    def make_question(self):
        messagebox.showinfo("Make Question", "Hier kun je een vraag maken.")
        self.current_question_count += 1
        self.question_count_label.config(text=f"Questions: {self.current_question_count}")

    def list_questions(self):
        messagebox.showinfo("List Questions", "Hier kun je alle vragen bekijken.")
        if self.current_question_count > 0:
            self.current_question_count -= 1
            self.question_count_label.config(text=f"Questions: {self.current_question_count}")

    def get_chapter_data(self, filename):
        try:
            if getattr(sys, 'frozen', False):
                current_directory = sys._MEIPASS
            else:
                current_directory = os.path.dirname(os.path.abspath(__file__))
            
            full_path = os.path.join(current_directory, 'assets', 'linux_questions', filename)
            
            with open(full_path, 'r') as file:
                data = json.load(file)
                return data['chapters'][0]
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def center_window(self):
        window_width = 1400
        window_height = 800
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def get_question_count(self, chapter_number):
        try:
            with open(os.path.join('assets', 'linux_questions', f"chapter{chapter_number}.json"), 'r') as file:
                data = json.load(file)
                return len(data['chapters'][0]['questions'])
        except (FileNotFoundError, json.JSONDecodeError):
            return 0

    def start_quiz(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            messagebox.showerror("Error", "Geen vragen gevonden in het geselecteerde hoofdstuk.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)
        
        self.shuffled_options = []
        for question in self.questions:
            options = list(question["options"])
            random.shuffle(options)
            self.shuffled_options.append(options)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = False

        # Set the session title according to the chapter data
        chapter_number = self.current_chapter_data.get('chapter', 'Unknown')
        chapter_title = self.current_chapter_data.get('description', 'Unknown Chapter')
        self.current_session_title = f"Chapter {chapter_number}: {chapter_title}"

        self.question_window()

    def start_assessment(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            messagebox.showerror("Error", "Geen vragen gevonden in de geselecteerde beoordeling.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)

        self.shuffled_options = []
        for question in self.questions:
            options = list(question["options"])
            random.shuffle(options)
            self.shuffled_options.append(options)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = True

        # Use a consistent session title format
        self.current_session_title = "Assessment 1 Questions"

        self.question_window()

    def start_assessment2(self):
        self.reset_statistics()

        filename = os.path.join('assets', 'linux_questions', "assessment2.json")
        try:
            with open(filename, 'r') as file:
                data = json.load(file)

            if 'chapters' not in data or len(data['chapters']) == 0:
                messagebox.showerror("Error", "'chapters' key not found in the JSON file.")
                return

            questions = data['chapters'][0]['questions']

            if len(questions) < 90:
                messagebox.showerror("Error", "Niet genoeg vragen beschikbaar na filtering.")
                return

            self.questions = random.sample(questions, 90)
            random.shuffle(self.questions)

            self.shuffled_options = []
            for question in self.questions:
                options = list(question["options"])
                random.shuffle(options)
                self.shuffled_options.append(options)

            self.current_question_index = 0
            self.user_answers = [None] * len(self.questions)
            self.session_active = True
            self.assessment_mode = True

            # Use a consistent session title format
            self.current_session_title = "Assessment 2 Questions"

            self.question_window()
        except (FileNotFoundError, json.JSONDecodeError) as e:
            messagebox.showerror("Error", f"Could not load assessment: {e}")

    def start_assessment3(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            messagebox.showerror("Error", "Geen vragen gevonden in de geselecteerde beoordeling.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)

        self.shuffled_options = []
        for question in self.questions:
            options = list(question["options"])
            random.shuffle(options)
            self.shuffled_options.append(options)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = True

        # Use a consistent session title format
        self.current_session_title = "Assessment 3 Questions"

        self.question_window()

    def start_exercise2(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            messagebox.showerror("Error", "No questions found in Exercise Chapter 2.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)
        
        self.shuffled_options = []
        for question in self.questions:
            options = list(question["options"])
            random.shuffle(options)
            self.shuffled_options.append(options)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = False

        # Set the session title using detailed information
        chapter_number = self.current_chapter_data.get('chapter', '2')
        chapter_title = self.current_chapter_data.get('description', 'Introduction to Services')
        self.current_session_title = f"Exercise Chapter {chapter_number}: {chapter_title}"

        self.question_window()
    
    def start_exercise3(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            messagebox.showerror("Error", "No questions found in Exercise Chapter 3.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)
        
        self.shuffled_options = []
        for question in self.questions:
            options = list(question["options"])
            random.shuffle(options)
            self.shuffled_options.append(options)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = False

        # Set the session title using detailed information
        chapter_number = self.current_chapter_data.get('chapter', '3')
        chapter_title = self.current_chapter_data.get('description', 'Managing Files, Directories, and Text')
        self.current_session_title = f"Exercise Chapter {chapter_number}: {chapter_title}"

        self.question_window()

    def start_exercise4(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            messagebox.showerror("Error", "No questions found in Exercise Chapter 4.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)
        
        self.shuffled_options = []
        for question in self.questions:
            options = list(question["options"])
            random.shuffle(options)
            self.shuffled_options.append(options)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = False

        # Set the session title using detailed information
        chapter_number = self.current_chapter_data.get('chapter', '4')
        chapter_title = self.current_chapter_data.get('description', 'Searching and Analyzing Text')
        self.current_session_title = f"Exercise Chapter {chapter_number}: {chapter_title}"

        self.question_window()

    def start_exercise5(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            messagebox.showerror("Error", "No questions found in Exercise Chapter 5.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)
        
        self.shuffled_options = []
        for question in self.questions:
            options = list(question["options"])
            random.shuffle(options)
            self.shuffled_options.append(options)

        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = False

        # Set the session title using detailed information
        chapter_number = self.current_chapter_data.get('chapter', '5')
        chapter_title = self.current_chapter_data.get('description', 'Explaining the Boot Process')
        self.current_session_title = f"Exercise Chapter {chapter_number}: {chapter_title}"

        self.question_window()  

    def question_window(self, title=None):
        self.question_win = tk.Toplevel(self.master)
        self.question_win.title("Quiz")
        self.question_win.geometry("1800x1200")
        self.question_win.protocol("WM_DELETE_WINDOW", self.close_question_window)

        # Use the current session title for the window title
        title_text = self.current_session_title if self.current_session_title else "Quiz"
        self.chapter_title_label = tk.Label(self.question_win, text=title_text, font=("Helvetica", 24, "bold"))
        self.chapter_title_label.pack(pady=10)

        self.question_counter = tk.Label(self.question_win, text=f"Question {self.current_question_index + 1} / {len(self.questions)}", font=("Helvetica", 18))
        self.question_counter.pack(pady=15)

        self.question_label = tk.Label(self.question_win, text=self.questions[self.current_question_index]["question"], wraplength=800, font=("Helvetica", 18))
        self.question_label.pack(pady=30)

        # Display question image if available
        self.display_question_image()

        self.var_list = []
        self.options_frame = tk.Frame(self.question_win)
        self.options_frame.pack(pady=15)

        saved_answers = self.user_answers[self.current_question_index]
        options = self.shuffled_options[self.current_question_index]

        for index, option in enumerate(options):
            var = tk.BooleanVar(value=(index in saved_answers if saved_answers is not None else False))
            checkbox = tk.Checkbutton(self.options_frame, text=option, variable=var, font=("Helvetica", 18))
            checkbox.pack(anchor="w")
            self.var_list.append(var)

        buttons_frame = tk.Frame(self.question_win)
        buttons_frame.pack(side="bottom", pady=(0, 120))

        self.submit_button = tk.Button(buttons_frame, text="Submit", font=("Helvetica", 16), command=self.submit_answer)
        self.submit_button.pack(side="top", padx=(37, 0), pady=(0, 30))

        self.previous_button = tk.Button(buttons_frame, text="Previous", font=("Helvetica", 16), command=self.previous_question)
        self.previous_button.pack(side="left", padx=25)

        self.stop_button = tk.Button(buttons_frame, text="Stop", font=("Helvetica", 16), command=self.show_stats)
        self.stop_button.pack(side="left", padx=25)

        self.exit_button = tk.Button(buttons_frame, text="Exit", font=("Helvetica", 16), command=self.exit_quiz)
        self.exit_button.pack(side="left", padx=25)

        self.next_button = tk.Button(buttons_frame, text="Next", font=("Helvetica", 16), command=self.next_question)
        self.next_button.pack(side="left", padx=25)

    def display_question_image(self):
        question = self.questions[self.current_question_index]
        image_path = question.get("image")

        if image_path:
            current_directory = os.path.dirname(os.path.abspath(__file__))
            full_image_path = os.path.join(current_directory, image_path)

            if os.path.exists(full_image_path):
                image = Image.open(full_image_path)
                image = image.resize((800, 300), Image.LANCZOS)
                self.question_image = ImageTk.PhotoImage(image)

                if hasattr(self, 'image_label') and self.image_label:
                    self.image_label.config(image=self.question_image)
                    self.image_label.image = self.question_image
                else:
                    self.image_label = tk.Label(self.question_win, image=self.question_image)
                    self.image_label.pack(pady=15, before=self.options_frame)
            else:
                if hasattr(self, 'image_label') and self.image_label:
                    self.image_label.pack_forget()
                    self.image_label = None
        else:
            if hasattr(self, 'image_label') and self.image_label:
                self.image_label.pack_forget()
                self.image_label = None

    def previous_question(self):
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.load_question()

    def next_question(self):
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.load_question()
        else:
            self.show_stats()

    def load_question(self):
        self.question_counter.config(text=f"Question {self.current_question_index + 1} / {len(self.questions)}")
        self.question_label.config(text=self.questions[self.current_question_index]["question"])

        for widget in self.options_frame.winfo_children():
            widget.destroy()

        self.var_list = []
        options = self.shuffled_options[self.current_question_index]
        
        saved_answers = self.user_answers[self.current_question_index]
        for index, option in enumerate(options):
            var = tk.BooleanVar(value=(index in saved_answers if saved_answers is not None else False))
            checkbox = tk.Checkbutton(self.options_frame, text=option, variable=var, font=("Helvetica", 18))
            checkbox.pack(anchor="w")
            self.var_list.append(var)

        # Reload the image for the new question
        self.display_question_image()

    def submit_answer(self):
        selected_answers = [index for index, var in enumerate(self.var_list) if var.get()]
        self.user_answers[self.current_question_index] = selected_answers

        correct_answer = self.questions[self.current_question_index]["answer"]

        if isinstance(correct_answer, list):
            correct_answer_indices = [self.shuffled_options[self.current_question_index].index(ans) for ans in correct_answer]
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
        self.question_win.destroy()
        self.add_image()
        messagebox.showinfo("Quiz Exited", "Quiz is exited. Returning to the main window.")

    def show_stats(self):
        self.question_win.destroy()
        self.stats_win = tk.Toplevel(self.master)
        self.stats_win.title("Statistics")
        self.stats_win.geometry("600x400")
        self.add_image()
        correct_count = sum(1 for score in self.correct_answers if score == 1.0)
        incorrect_count = sum(1 for score in self.correct_answers if score == 0.0)
        skipped_count = sum(1 for answer in self.user_answers if answer is None)
        total_count = len(self.questions)
        total_score = sum(self.correct_answers)
        percentage_correct = (total_score / total_count * 100) if total_count > 0 else 0

        stats_label = tk.Label(self.stats_win, text=f"You scored {total_score:.2f} out of {total_count} correct!", font=("Helvetica", 22))
        stats_label.pack(pady=10)

        tk.Label(self.stats_win).pack(pady=5)
        tk.Label(self.stats_win, text=f"Correct Answers: {correct_count}", font=("Helvetica", 18)).pack(pady=5)
        tk.Label(self.stats_win, text=f"Incorrect Answers: {incorrect_count}", font=("Helvetica", 18)).pack(pady=5)
        tk.Label(self.stats_win, text=f"Skipped Questions: {skipped_count}", font=("Helvetica", 18)).pack(pady=5)

        tk.Label(self.stats_win).pack(pady=10)
        tk.Label(self.stats_win, text=f"Score: {percentage_correct:.2f} %", font=("Helvetica", 18)).pack(pady=5)

        nav_frame = tk.Frame(self.stats_win)
        nav_frame.pack(side="bottom", pady=(20, 20))

        review_button = tk.Button(nav_frame, text="Review Answers", font=("Helvetica", 18), command=self.review_answers)
        review_button.pack(side="left", padx=20)

        finish_button = tk.Button(nav_frame, text="Finish", font=("Helvetica", 18), command=self.close_stats_window)
        finish_button.pack(side="left", padx=20)

    def review_answers(self):
        self.stats_win.destroy()
        self.current_question_index = 0
        self.review_question_window()

    def review_question_window(self):
        self.review_win = tk.Toplevel(self.master)
        self.review_win.title("Review Answers")
        self.review_win.geometry("1800x1200")

        # Use the current session title for the review window
        title_text = self.current_session_title if self.current_session_title else "Review Answers"
        self.chapter_title_label = tk.Label(self.review_win, text=title_text, font=("Helvetica", 24, "bold"))
        self.chapter_title_label.pack(pady=10)

        self.question_counter_review = tk.Label(self.review_win, text=f"Question {self.current_question_index + 1} / {len(self.questions)}", font=("Helvetica", 18))
        self.question_counter_review.pack(pady=15)

        self.review_question_label = tk.Label(self.review_win, text=self.questions[self.current_question_index]["question"], wraplength=700, font=("Helvetica", 18))
        self.review_question_label.pack(pady=30)

        # Display question image in review
        self.display_question_image_review()

        self.options_frame = tk.Frame(self.review_win)
        self.options_frame.pack(pady=15)

        self.load_review_question()

        nav_frame = tk.Frame(self.review_win)
        nav_frame.pack(side="bottom", pady=(0, 120))

        self.previous_review_button = tk.Button(nav_frame, text="Previous", font=("Helvetica", 18), command=self.previous_review_question)
        self.previous_review_button.pack(side="left", padx=30)

        self.next_review_button = tk.Button(nav_frame, text="Next", font=("Helvetica", 18), command=self.next_review_question)
        self.next_review_button.pack(side="left", padx=30)

        self.stats_button = tk.Button(nav_frame, text="Statistics", font=("Helvetica", 18), command=self.show_stats_from_review)
        self.stats_button.pack(side="left", padx=30)

        self.finish_review_button = tk.Button(nav_frame, text="Finish", font=("Helvetica", 18), command=self.finish_review)
        self.finish_review_button.pack(side="left", padx=30)

    def display_question_image_review(self):
        question = self.questions[self.current_question_index]
        image_path = question.get("image")

        if image_path:
            current_directory = os.path.dirname(os.path.abspath(__file__))
            full_image_path = os.path.join(current_directory, image_path)

            if os.path.exists(full_image_path):
                image = Image.open(full_image_path)
                image = image.resize((800, 300), Image.LANCZOS)
                self.review_photo = ImageTk.PhotoImage(image)

                if hasattr(self, 'review_image_label') and self.review_image_label:
                    self.review_image_label.config(image=self.review_photo)
                    self.review_image_label.image = self.review_photo
                else:
                    self.review_image_label = tk.Label(self.review_win, image=self.review_photo)
                    self.review_image_label.pack(before=self.options_frame)
            else:
                if hasattr(self, 'review_image_label') and self.review_image_label:
                    self.review_image_label.pack_forget()
                    self.review_image_label = None
        else:
            if hasattr(self, 'review_image_label') and self.review_image_label:
                self.review_image_label.pack_forget()
                self.review_image_label = None

    def show_stats_from_review(self):
        self.review_win.destroy()
        self.show_stats()

    def previous_review_question(self):
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.load_review_question()

    def next_review_question(self):
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.load_review_question()
        else:
            self.close_review_window()

    def load_review_question(self):
        self.current_question = self.questions[self.current_question_index]  # Zorg ervoor dat current_question correct is ingesteld
        
        self.review_question_label.config(text=self.current_question["question"])
        self.question_counter_review.config(text=f"Question {self.current_question_index + 1} / {len(self.questions)}")

        for widget in self.options_frame.winfo_children():
            widget.destroy()

        correct_answers = self.current_question["answer"]
        user_selected = self.user_answers[self.current_question_index] if self.user_answers[self.current_question_index] is not None else []

        options = self.shuffled_options[self.current_question_index]

        if isinstance(correct_answers, list):
            correct_answers_set = set(correct_answers)
        else:
            correct_answers_set = {correct_answers}

        for index, option in enumerate(options):
            is_correct = option in correct_answers_set
            user_selected_correct = index in user_selected

            if user_selected_correct and is_correct:
                answer_label = tk.Label(self.options_frame, text=f"[Correct ✓] {option}", fg="green", font=("Helvetica", 18, "bold"))
                explanation_label = tk.Label(self.options_frame, text=self.current_question.get("explanation", {}).get(option, ""), fg="black", font=("Helvetica", 16))
            elif user_selected_correct and not is_correct:
                answer_label = tk.Label(self.options_frame, text=f"[Incorrect X] {option}", fg="red", font=("Helvetica", 18, "bold"))
                explanation_label = tk.Label(self.options_frame, text=self.current_question.get("explanation", {}).get(option, ""), fg="black", font=("Helvetica", 16))
            elif not user_selected_correct and is_correct:
                answer_label = tk.Label(self.options_frame, text=f"{option}", fg="green", font=("Helvetica", 18))
                explanation_label = tk.Label(self.options_frame, text=self.current_question.get("explanation", {}).get(option, ""), fg="black", font=("Helvetica", 16))
            else:
                answer_label = tk.Label(self.options_frame, text=f"{option}", fg="red", font=("Helvetica", 18))
                explanation_label = tk.Label(self.options_frame, text=self.current_question.get("explanation", {}).get(option, ""), fg="black", font=("Helvetica", 16))

            answer_label.pack(anchor="w")
            explanation_label.pack(anchor="w", pady=(0, 5))

        # Laad de afbeelding voor de vraag
        self.display_question_image_review()

    def finish_review(self):
        self.close_review_window()
        self.session_active = False

    def close_question_window(self):
        self.question_win.destroy()

    def close_stats_window(self):
        self.stats_win.destroy()

    def close_review_window(self):
        self.review_win.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()