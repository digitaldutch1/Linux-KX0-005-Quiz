


import tkinter as tk
from tkinter import messagebox
import json
import random
import webbrowser
import os

def load_questions_from_json(filename):
    try:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(current_directory, filename)

        with open(full_path, 'r') as file:
            data = json.load(file)
            return data['chapters'][0]  # Neem het eerste hoofdstuk
    except (FileNotFoundError, json.JSONDecodeError) as e:
        messagebox.showerror("Error", f"Could not load questions: {e}")
    return {}

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
        self.assessment_mode = False  # Voeg een vlag toe om de beoordeling te volgen

        self.center_window()

        self.banner = tk.Label(self.master, text="Linux+ KX0-005", font=("Helvetica", 40, "bold"))
        self.banner.pack(pady=20)

        self.navbar_frame = tk.Frame(self.master)
        self.navbar_frame.pack()

        self.ebook_menu = tk.Menubutton(self.navbar_frame, text="Ebook", font=("Helvetica", 26), relief="raised", borderwidth=1)
        self.ebook_menu.menu = tk.Menu(self.ebook_menu, tearoff=0, font=("Helvetica", 18))
        self.ebook_menu["menu"] = self.ebook_menu.menu
        self.ebook_menu.pack(side="left", padx=20)

        self.ebook_menu.menu.add_command(label="Linux +", command=self.open_ebook)

        self.chapter_menu = tk.Menubutton(self.navbar_frame, text="Chapters", font=("Helvetica", 26), relief="raised", borderwidth=1)
        self.chapter_menu.menu = tk.Menu(self.chapter_menu, tearoff=0, font=("Helvetica", 18))
        self.chapter_menu["menu"] = self.chapter_menu.menu
        self.chapter_menu.pack(side="left", padx=20)

        for i in range(2, 31):
            chapter_data = self.get_chapter_data(f"linux_questions/chapter{i}.json")
            chapter_title = chapter_data['description'] if chapter_data else f"Title of Chapter {i}"
            question_count = self.get_question_count(i)

            self.chapter_menu.menu.add_command(
                label=f"Chapter {i}: {chapter_title} ({question_count})",
                command=lambda i=i: self.start_quiz(f"linux_questions/chapter{i}.json")
            )

        self.assessment_menu = tk.Menubutton(self.navbar_frame, text="Assessment", font=("Helvetica", 26), relief="raised", borderwidth=1)
        self.assessment_menu.menu = tk.Menu(self.assessment_menu, tearoff=0, font=("Helvetica", 18))
        self.assessment_menu["menu"] = self.assessment_menu.menu
        self.assessment_menu.pack(side="left", padx=20)

        self.assessment_menu.menu.add_command(
            label="Assessment 1 (56)",
            command=lambda: self.start_assessment("linux_questions/assessment1.json")
        )

        self.assessment_menu.menu.add_command(
            label="Assessment 2 (90)",
            command=self.start_assessment2
        )

    def open_ebook(self):
        current_directory = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(current_directory, 'linuxbook', 'linuxbook.pdf')

        if os.path.exists(pdf_path):
            webbrowser.open(pdf_path)
        else:
            messagebox.showerror("Error", "Ebook niet gevonden.")

    def get_chapter_data(self, filename):
        try:
            current_directory = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(current_directory, filename)
            
            with open(full_path, 'r') as file:
                data = json.load(file)
                return data['chapters'][0]  # Neem het eerste hoofdstuk
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def center_window(self):
        window_width = 1200
        window_height = 800
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def get_question_count(self, chapter_number):
        try:
            with open(f"linux_questions/chapter{chapter_number}.json", 'r') as file:
                data = json.load(file)
                return len(data['chapters'][0]['questions'])  # Aantal vragen in het hoofdstuk
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
        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = False  # Zet assessment mode uit
        self.question_window()

    def start_assessment(self, filename):
        self.reset_statistics()
        self.current_chapter_data = load_questions_from_json(filename)

        if not self.current_chapter_data or "questions" not in self.current_chapter_data:
            messagebox.showerror("Error", "Geen vragen gevonden in de geselecteerde beoordeling.")
            return

        self.questions = self.current_chapter_data['questions']
        random.shuffle(self.questions)
        self.current_question_index = 0
        self.user_answers = [None] * len(self.questions)
        self.session_active = True
        self.assessment_mode = True  # Zet assessment mode aan
        self.question_window(title="Assessment 1 Questions")

    def start_assessment2(self):
        self.reset_statistics()

        filename = "linux_questions/assessment2.json"
        try:
            with open(filename, 'r') as file:
                data = json.load(file)

                if 'chapters' not in data or len(data['chapters']) == 0:
                    messagebox.showerror("Error", "'chapters' key not found in the JSON file.")
                    return
                
                questions = data['chapters'][0]['questions']
                questions = [q for q in questions if q['number'] != 104]

                if len(questions) < 90:
                    messagebox.showerror("Error", "Niet genoeg vragen beschikbaar na filtering.")
                    return
                
                self.questions = random.sample(questions, 90)
                random.shuffle(self.questions)

                self.current_question_index = 0
                self.user_answers = [None] * len(self.questions)
                self.session_active = True
                self.assessment_mode = True  # Zet assessment mode aan
                self.question_window(title="Assessment 2 Questions")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            messagebox.showerror("Error", f"Could not load assessment: {e}")

    def question_window(self, title=None):
        self.question_win = tk.Toplevel(self.master)
        self.question_win.title("Quiz")
        self.question_win.geometry("1200x1000")
        self.question_win.protocol("WM_DELETE_WINDOW", self.close_question_window)

        # Hoofdstuktitel
        if self.assessment_mode:
            title_text = title if title else "Assessment Questions"
        else:
            chapter_number = self.current_chapter_data['chapter'] if self.current_chapter_data else ""
            chapter_title = self.current_chapter_data['description'] if self.current_chapter_data else "Assessment"
            title_text = f"Chapter {chapter_number}: {chapter_title}" if title is None else title

        self.chapter_title_label = tk.Label(self.question_win, text=title_text, font=("Helvetica", 24, "bold"))
        self.chapter_title_label.pack(pady=10)

        self.question_counter = tk.Label(self.question_win, text=f"Question {self.current_question_index + 1} / {len(self.questions)}", font=("Helvetica", 18))
        self.question_counter.pack(pady=15)

        self.question_label = tk.Label(self.question_win, text=self.questions[self.current_question_index]["question"], wraplength=800, font=("Helvetica", 18))
        self.question_label.pack(pady=30)

        self.var_list = []
        self.options_frame = tk.Frame(self.question_win)
        self.options_frame.pack()

        saved_answers = self.user_answers[self.current_question_index]
        for index, option in enumerate(self.questions[self.current_question_index]["options"]):
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

        self.stop_button = tk.Button(buttons_frame, text="Stop", font=("Helvetica", 16), command=self.stop_quiz)
        self.stop_button.pack(side="left", padx=25)

        self.next_button = tk.Button(buttons_frame, text="Next", font=("Helvetica", 16), command=self.next_question)
        self.next_button.pack(side="left", padx=25)

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
        saved_answers = self.user_answers[self.current_question_index]
        for index, option in enumerate(self.questions[self.current_question_index]["options"]):
            var = tk.BooleanVar(value=(index in saved_answers if saved_answers is not None else False))
            checkbox = tk.Checkbutton(self.options_frame, text=option, variable=var, font=("Helvetica", 18))
            checkbox.pack(anchor="w")
            self.var_list.append(var)

    def submit_answer(self):
        selected_answers = [index for index, var in enumerate(self.var_list) if var.get()]
        self.user_answers[self.current_question_index] = selected_answers

        correct_answer = self.questions[self.current_question_index]["answer"]

        if isinstance(correct_answer, list):
            if set(selected_answers) == set(correct_answer):
                self.correct_answers.append(True)
            else:
                self.correct_answers.append(False)
        else:
            if selected_answers == [self.questions[self.current_question_index]["options"].index(correct_answer)]:
                self.correct_answers.append(True)
            else:
                self.correct_answers.append(False)

        if self.current_question_index < len(self.questions) - 1:
            self.next_question()
        else:
            self.show_stats()

    def reset_statistics(self):
        self.correct_answers = []
        self.user_answers = []

    def stop_quiz(self):
        self.session_active = False
        self.question_win.destroy()
        messagebox.showinfo("Quiz Stopped", "Quiz is stopped. Returning to the main window.")

    def show_stats(self):
        self.question_win.destroy()
        self.stats_win = tk.Toplevel(self.master)
        self.stats_win.title("Statistics")
        self.stats_win.geometry("600x400")
        correct_count = sum(self.correct_answers)
        incorrect_count = len(self.questions) - correct_count - sum(1 for answer in self.user_answers if answer is None)
        skipped_count = sum(1 for answer in self.user_answers if answer is None)
        total_count = len(self.questions)
        percentage_correct = (correct_count / total_count * 100) if total_count > 0 else 0

        stats_label = tk.Label(self.stats_win, text=f"You got {correct_count} out of {total_count} correct!", font=("Helvetica", 22))
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

        # Hoofdstuktitel met nummer
        if self.assessment_mode:
            title_text = "Assessment Questions"
        else:
            chapter_number = self.current_chapter_data['chapter']
            chapter_title = self.current_chapter_data['description']
            title_text = f"Chapter {chapter_number}: {chapter_title}"

        self.chapter_title_label = tk.Label(self.review_win, text=title_text, font=("Helvetica", 24, "bold"))
        self.chapter_title_label.pack(pady=10)

        self.question_counter_review = tk.Label(self.review_win, text=f"Question {self.current_question_index + 1} / {len(self.questions)}", font=("Helvetica", 18))
        self.question_counter_review.pack(pady=15)

        self.review_question_label = tk.Label(self.review_win, text=self.questions[self.current_question_index]["question"], wraplength=700, font=("Helvetica", 18))
        self.review_question_label.pack(pady=30)

        self.options_frame = tk.Frame(self.review_win)
        self.options_frame.pack()

        self.load_review_question()

        nav_frame = tk.Frame(self.review_win)
        nav_frame.pack(side="bottom", pady=(0, 180))

        self.previous_review_button = tk.Button(nav_frame, text="Previous", font=("Helvetica", 18), command=self.previous_review_question)
        self.previous_review_button.pack(side="left", padx=30)

        self.next_review_button = tk.Button(nav_frame, text="Next", font=("Helvetica", 18), command=self.next_review_question)
        self.next_review_button.pack(side="left", padx=30)

        self.finish_review_button = tk.Button(nav_frame, text="Finish", font=("Helvetica", 18), command=self.finish_review)
        self.finish_review_button.pack(side="left", padx=30)

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
        self.review_question_label.config(text=self.questions[self.current_question_index]["question"])
        self.question_counter_review.config(text=f"Question {self.current_question_index + 1} / {len(self.questions)}")

        for widget in self.options_frame.winfo_children():
            widget.destroy()

        correct_answers = self.questions[self.current_question_index]["answer"]
        user_selected = self.user_answers[self.current_question_index] if self.user_answers[self.current_question_index] is not None else []

        if isinstance(correct_answers, list):
            correct_answers_set = set(correct_answers)
        else:
            correct_answers_set = {correct_answers}

        for index, option in enumerate(self.questions[self.current_question_index]["options"]):
            is_correct = option in correct_answers_set
            user_selected_correct = index in user_selected
            
            if user_selected_correct and is_correct:
                answer_label = tk.Label(self.options_frame, text=f"[Correct ✓] {option}", fg="green", font=("Helvetica", 18, "bold"))
                explanation_label = tk.Label(self.options_frame, text=self.questions[self.current_question_index]["explanation"][option], fg="black", font=("Helvetica", 16))
            elif user_selected_correct and not is_correct:
                answer_label = tk.Label(self.options_frame, text=f"[Incorrect X] {option}", fg="red", font=("Helvetica", 18, "bold"))
                explanation_label = tk.Label(self.options_frame, text=self.questions[self.current_question_index]["explanation"][option], fg="black", font=("Helvetica", 16))
            elif not user_selected_correct and is_correct:
                answer_label = tk.Label(self.options_frame, text=f"{option}", fg="green", font=("Helvetica", 18))
                explanation_label = tk.Label(self.options_frame, text=self.questions[self.current_question_index]["explanation"][option], fg="black", font=("Helvetica", 16))
            else:
                answer_label = tk.Label(self.options_frame, text=f"{option}", fg="red", font=("Helvetica", 18))
                explanation_label = tk.Label(self.options_frame, text=self.questions[self.current_question_index]["explanation"][option], fg="black", font=("Helvetica", 16))

            answer_label.pack(anchor="w")
            explanation_label.pack(anchor="w", pady=5)
            tk.Label(self.options_frame).pack()

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