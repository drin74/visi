from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
import random


class HangmanGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Виселица")
        self.root.geometry("900x700")

        self.conn = sqlite3.connect('visi.db')
        self.cursor = self.conn.cursor()

        self.current_word = ""
        self.current_category = ""
        self.guessed_letters = []
        self.mistakes = []
        self.attempts_left = 6
        self.game_active = False
        self.letter_buttons = []

        try:
            image = Image.open("image/squared-paper-sheet-notebook-background-for-school-vector.png")
            self.background_image = ImageTk.PhotoImage(image)
        except:
            self.background_image = None

        self.show_main_menu()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.canvas = Canvas(self.root, width=900, height=700)
        self.canvas.pack(fill="both", expand=True)

        if self.background_image:
            self.canvas.create_image(0, 0, image=self.background_image, anchor="nw")
        else:
            self.canvas.configure(bg="#f5f5dc")

    def get_categories(self):
        self.cursor.execute("SELECT DISTINCT category FROM nems ORDER BY category")
        return [row[0] for row in self.cursor.fetchall()]

    def get_random_word(self, category):
        self.cursor.execute(
            "SELECT slovo FROM nems WHERE category = ? ORDER BY RANDOM() LIMIT 1",
            (category,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None

    def show_main_menu(self):
        self.clear_window()

        title_bg = self.canvas.create_rectangle(
            200, 25, 700, 125,
            fill="white",
            outline="#95a5a6",
            width=2
        )

        title = Label(
            self.canvas,
            text="ВИСЕЛИЦА",
            font=("Arial", 48, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        self.canvas.create_window(450, 75, window=title)

        play_btn = Button(
            self.canvas,
            text="🎮 ИГРАТЬ",
            font=("Arial", 26, "bold"),
            bg="#27ae60",
            fg="white",
            padx=50,
            pady=18,
            bd=0,
            cursor="hand2",
            activebackground="#2ecc71",
            command=self.show_categories
        )
        self.canvas.create_window(450, 280, window=play_btn)

        exit_btn = Button(
            self.canvas,
            text="❌ ВЫХОД",
            font=("Arial", 18, "bold"),
            bg="#e74c3c",
            fg="white",
            padx=30,
            pady=10,
            bd=0,
            cursor="hand2",
            command=self.root.quit
        )
        self.canvas.create_window(450, 380, window=exit_btn)

    def show_categories(self):
        self.clear_window()
        title_bg = self.canvas.create_rectangle(
            200, 10, 700, 85,
            fill="white",
            outline="#95a5a6",
            width=2
        )

        title = Label(
            self.canvas,
            text="ВЫБЕРИ ТЕМУ",
            font=("Arial", 32, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        self.canvas.create_window(450, 55, window=title)


        categories = self.get_categories()

        start_y = 120
        for i, category in enumerate(categories):
            btn = Button(
                self.canvas,
                text=category,
                font=("Courier", 15, "bold"),
                bg="#3498db",
                fg="white",
                padx=20,
                pady=8,
                bd=0,
                cursor="hand2",
                activebackground="#2980b9",
                width=28,
                command=lambda c=category: self.start_game(c)
            )
            self.canvas.create_window(450, start_y + i * 55, window=btn)

        back_btn = Button(
            self.canvas,
            text="← НАЗАД",
            font=("Arial", 12, "bold"),
            bg="#95a5a6",
            fg="white",
            padx=20,
            pady=8,
            bd=0,
            cursor="hand2",
            command=self.show_main_menu
        )
        self.canvas.create_window(80, 630, window=back_btn)

    def start_game(self, category):
        self.clear_window()
        self.current_category = category


        self.current_word = self.get_random_word(category)

        if not self.current_word:
            messagebox.showerror("Ошибка", f"Нет слов в категории {category}")
            self.show_categories()
            return

        self.guessed_letters = ["_"] * len(self.current_word)
        self.mistakes = []
        self.attempts_left = 6
        self.game_active = True
        self.letter_buttons = []

        self.create_game_interface()

        self.update_display()
        self.draw_hangman()

    def create_game_interface(self):

        back_btn = Button(
            self.canvas,
            text="← МЕНЮ",
            font=("Arial", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            padx=15,
            pady=5,
            bd=0,
            cursor="hand2",
            command=self.show_main_menu
        )
        self.canvas.create_window(55, 30, window=back_btn)


        self.hangman_canvas = Canvas(
            self.canvas,
            width=250,
            height=250,
            bg="white",
            highlightthickness=2,
            highlightbackground="#95a5a6"
        )
        self.canvas.create_window(150, 200, window=self.hangman_canvas)

        self.word_label = Label(
            self.canvas,
            text="",
            font=("Courier", 30, "bold"),
            bg="white",
            fg="#27ae60"
        )
        self.canvas.create_window(550, 180, window=self.word_label)

        mistakes_bg = self.canvas.create_rectangle(
            400, 220, 790, 265,
            fill="white",
            outline="#95a5a6",
            width=1
        )

        self.mistakes_label = Label(
            self.canvas,
            text="Ошибки: ",
            font=("Courier", 15, "bold"),
            bg="white",
            fg="#e74c3c"
        )
        self.canvas.create_window(550, 242, window=self.mistakes_label)

        attempts_bg = self.canvas.create_rectangle(
            490, 265, 670, 300,
            fill="white",
            outline="#95a5a6",
            width=1
        )

        self.attempts_label = Label(
            self.canvas,
            text=f"Попыток: {self.attempts_left}",
            font=("Courier", 15, "bold"),
            bg="white",
            fg="#3498db"
        )
        self.canvas.create_window(560, 282, window=self.attempts_label)

        self.create_keyboard()

    def create_keyboard(self):
        letters = [
            ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё'],
            ['Ж', 'З', 'И', 'Й', 'К', 'Л', 'М'],
            ['Н', 'О', 'П', 'Р', 'С', 'Т', 'У'],
            ['Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ'],
            ['Ы', 'Ь', 'Э', 'Ю', 'Я']
        ]

        start_y = 450
        for i, row in enumerate(letters):
            start_x = 400
            for j, letter in enumerate(row):
                btn = Button(
                    self.canvas,
                    text=letter,
                    font=("Arial", 11, "bold"),
                    width=3,
                    height=1,
                    bg="#61F689",
                    fg="#2c3e50",
                    relief="raised",
                    cursor="hand2",
                    command=lambda l=letter: self.guess_letter(l)
                )
                self.canvas.create_window(start_x + j * 45, start_y + i * 45, window=btn)
                self.letter_buttons.append(btn)

    def update_display(self):
        self.word_label.config(text=" ".join(self.guessed_letters))

        mistakes_text = ", ".join(self.mistakes) if self.mistakes else ""
        self.mistakes_label.config(text=f"Ошибки: {mistakes_text}")
        self.attempts_label.config(text=f"Попыток: {self.attempts_left}")

    def guess_letter(self, letter):
        if not self.game_active:
            return

        for btn in self.letter_buttons:
            if btn['text'] == letter:
                btn.config(state="disabled", bg="#bdc3c7")
                break

        if letter in self.guessed_letters or letter in self.mistakes:
            return

        if letter in self.current_word:
            for i, char in enumerate(self.current_word):
                if char == letter:
                    self.guessed_letters[i] = letter
            self.update_display()

            if "_" not in self.guessed_letters:
                self.game_active = False
                messagebox.showinfo("Победа!", f"Вы выиграли! Слово: {self.current_word}")
                self.ask_next_game()
        else:
            self.mistakes.append(letter)
            self.attempts_left -= 1
            self.update_display()
            self.draw_hangman()

            # Проверка поражения
            if self.attempts_left == 0:
                self.game_active = False
                messagebox.showinfo("Поражение!", f"Вы проиграли! Слово: {self.current_word}")
                self.ask_next_game()

    def draw_hangman(self):
        self.hangman_canvas.delete("all")

        self.hangman_canvas.create_line(40, 220, 120, 220, width=3)
        self.hangman_canvas.create_line(80, 220, 80, 50, width=3)
        self.hangman_canvas.create_line(80, 50, 160, 50, width=3)
        self.hangman_canvas.create_line(160, 50, 160, 75, width=2)

        if self.attempts_left <= 5:
            self.hangman_canvas.create_oval(145, 75, 175, 105, width=2)
        if self.attempts_left <= 4:
            self.hangman_canvas.create_line(160, 105, 160, 155, width=2)
        if self.attempts_left <= 3:
            self.hangman_canvas.create_line(160, 120, 140, 140, width=2)
        if self.attempts_left <= 2:
            self.hangman_canvas.create_line(160, 120, 180, 140, width=2)
        if self.attempts_left <= 1:
            self.hangman_canvas.create_line(160, 155, 140, 180, width=2)
        if self.attempts_left <= 0:
            self.hangman_canvas.create_line(160, 155, 180, 180, width=2)

    def ask_next_game(self):
        result = messagebox.askyesno("Новая игра", "Хотите сыграть ещё раз?")
        if result:
            self.show_categories()
        else:
            self.show_main_menu()


# Запуск
if __name__ == "__main__":
    root = Tk()
    game = HangmanGame(root)
    root.mainloop()