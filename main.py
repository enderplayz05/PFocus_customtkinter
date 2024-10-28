#This build uses a different gui library, its customized version of tkinter, that still retains functions of tkinter
#which means still has the limited capabilities as tkinter, which custtomtkinter adds modern aethestics, which means it doesn't 
#extend core functionalities

import customtkinter as ctk             # changed from tkinter to customtkinter
from CTkListbox import *                # separate library from customtkinter, extension for customtkinter in making listboxs
from CTkMessagebox import CTkMessagebox # Import CTkMessagebox instead of messagebox
from tkinter import PhotoImage
import time
import threading
import pygame
from pygame import mixer

# Alarm from usage of pygame library
pygame.mixer.init()
alarm_sound = pygame.mixer.Sound("alarm.wav")

class PomodoroApp(ctk.CTk):  

    def __init__(self):
        super().__init__()
        self.title("PFocus")
        self.geometry("400x500")
        self.config(bg="#000000")
        self.resizable(False, False)  # This disables the option for fullscreen mode
        self.icon = PhotoImage(file='icon.png')  # Icon initialization
        self.iconphoto(False, self.icon)  # applying Icon
        self.default_work_time = 25 * 60  # Default: 25 minutes in seconds
        self.default_break_time = 5 * 60  # Default: 5 minutes in seconds
        self.current_time = self.default_work_time
        self.is_work_time = True
        self.timer_running = False
        self.completed_cycles = 0
        self.task_array = []

        # Cycle Counter
        self.cycle_counter_label = ctk.CTkLabel(self, text=f"Cycles: {self.completed_cycles}", bg_color="#000000", text_color="#ffd700")
        self.cycle_counter_label.place(x=320, y=10)

        # Timer Display
        self.timer_label = ctk.CTkLabel(self, text=self.format_time(self.current_time), font=("Roboto", 48),fg_color="#000000",bg_color="#000000",text_color="#ffd700")     #root label of clock timer, it also contains aethetics attributes
        self.timer_label.place(x=145, y=40)  #Top placement using x and y coordinates

        # Start/Stop Button
        self.start_stop_button = ctk.CTkButton(self, text="Start",text_color="#000000", command=self.toggle_timer, fg_color="#ffd700",bg_color="#000000",corner_radius=30)
        self.start_stop_button.pack(pady=110)
        self.start_stop_button.configure(width=75, height=30) 

        # Timer Customization
        self.work_time_input = ctk.CTkEntry(self, font=('Arial', 20), width=180,fg_color="#1e1e1e",bg_color="#000000",border_color="#000000",corner_radius=30)      #root of work in minutes input, it also contains design attributes
        self.work_time_input_label = ctk.CTkLabel(self, text="Work in Minutes", text_color="#ffd700",font=("Arial", 14),fg_color="#000000",bg_color="#000000")      #root of label for work in minutes, it also cantains design attribute
        self.work_time_input.insert(0, "")                          #where user types the work in minutes
        self.work_time_input_label.place(x=25, y=178)               #places the break in minutes on middle left, also in same alignment               
        self.work_time_input.place(anchor="ne", x=350,y=178)        #places the INPUT break in minutes on middle right, also in same alignment

        self.break_time_input = ctk.CTkEntry(self, font=('Arial', 20), width=180,fg_color="#1e1e1e",bg_color="#000000",border_color="#000000",corner_radius=30)     #root of break in minutes input, which means which means its the box that you can have user input
        self.break_time_input_label = ctk.CTkLabel(self, text="Break in Minutes", text_color="#ffd700",font=("Arial", 14),fg_color="#000000",bg_color="#000000")    #root of label for break in minutes
        self.break_time_input.insert(0, "")                         #where user types the break in minutes
        self.break_time_input_label.place(x=20, y=225)              #places the break in minutes on middle left 
        self.break_time_input.place(anchor="ne",x=350,y=225)        #places the INPUT break in minutes on middle right

        set_timer_button = ctk.CTkButton(self, text="Set Timer", text_color="#000000",command=self.set_custom_times,fg_color="#ffd700",bg_color="#000000",corner_radius=30)     #root of timer button, has design attributes
        set_timer_button.place(y=265,x=165)                         #places on the center of the entire window
        set_timer_button.configure(width=60, height=20)             #size of the set timer button

        # Task Input
        self.task_input_label = ctk.CTkLabel(self, text="ADD A TASK", text_color="#ffd700",font=("Arial", 14),fg_color="#000000",bg_color="#000000")                            #root of label for add a task,, also contains design attributes 
        self.task_input = ctk.CTkEntry(self, font=('Arial', 20), width=180,fg_color="#1e1e1e",bg_color="#000000",border_color="#000000",corner_radius=30)                       #root of task input, also contains design attributes
        self.task_input.insert(0, "")                       #where user types the task
        self.task_input_label.place(x=30, y=325)            #places the add a task label on the bottom center 
        self.task_input.place(anchor="ne", x=350, y=325)    #places the task input near the bottom on the right

        add_task_button = ctk.CTkButton(self, text="Add Task", text_color="#000000",command=self.add_task,fg_color="#ffd700",bg_color="#000000",corner_radius=30)           #root of add task button, also has attributes       
        add_task_button.place(x=150,y=370)                          #place the button near the bottom
        add_task_button.configure(width=75, height=20)              #size of the add tasj button

        # Task List
        self.task_list = CTkListbox(self, justify="center", font=("Arial", 20), width=300, height=50, bg_color="#1e1e1e", border_color="#1e1e1e", fg_color="#1e1e1e")
        self.task_list.pack(fill="x", expand=True)      #this makes sure that it expands the table where the tak are
        self.task_list.place(x=40, y=410)               #place the task table at the bottom

        self.protocol("WM_DELETE_WINDOW", self.on_closing)          #garbage collection

    def format_time(self, seconds):                     #function formats time to MM:SS
        minutes, seconds = divmod(seconds, 60)
        return f"{int(minutes):02}:{int(seconds):02}"

    def toggle_timer(self):                             #function to determine when time is running
        if self.timer_running:
            self.timer_running = False
            self.start_stop_button.configure(text="Start")
        else:
            self.timer_running = True
            self.start_stop_button.configure(text="Pause")
            self.run_timer()

    def run_timer(self):                               #handles count down; when true, starts timer only if self.timer_running is true and the current time is greater than 0, if it is then timer will go down in seconds
        def update_timer():
            while self.timer_running and self.current_time > 0:
                self.current_time -= 1
                self.timer_label.configure(text=self.format_time(self.current_time))
                time.sleep(1)

            if self.current_time <= 0:
                self.show_alarm()

        timer_thread = threading.Thread(target=update_timer)            #makes sure to update the timer
        timer_thread.start()

    def set_custom_times(self):
        try:
            work_minutes = int(self.work_time_input.get())
            break_minutes = int(self.break_time_input.get())
            if work_minutes > 0:
                self.default_work_time = work_minutes * 60
            if break_minutes > 0:
                self.default_break_time = break_minutes * 60
            self.current_time = self.default_work_time
            self.timer_label.configure(text=self.format_time(self.current_time))
        except ValueError:
            CTkMessagebox(title="Invalid Input", message="Please enter valid numbers.")

    def add_task(self):                             #function for adding a task
        task_text = self.task_input.get().strip()
        if task_text:
            # Add task to the array
            self.task_array.append(task_text)
            # Update the Listbox display
            self.update_task_list_display()
            # Clear input field
            self.task_input.delete(0, ctk.END)

    def update_task_list_display(self):
        # Clear the Listbox
        self.task_list.delete(0, ctk.END)
        # Insert all tasks from the array into the Listbox
        for task in self.task_array:
            self.task_list.insert(ctk.END, task)

    def remove_task(self, index):
        # Remove task from array if index is valid
        if 0 <= index < len(self.task_array):
            del self.task_array[index]
            # Update Listbox display
            self.update_task_list_display()

    def show_alarm(self):
        self.timer_running = False
        self.start_stop_button.configure(text="Pause")
        pygame.mixer.Sound.play(alarm_sound)

        # Alarm notification
        msg = CTkMessagebox(title="Time's Up", message="The timer has ended!",option_1="confirm")
        responses = msg.get()
        if responses == "confirm":
            # Switch between work and break time
            self.is_work_time = not self.is_work_time
            self.current_time = self.default_work_time if self.is_work_time else self.default_break_time
            if self.is_work_time:
                self.completed_cycles += 1
                self.cycle_counter_label.configure(text=f"Cycles: {self.completed_cycles}")
            self.timer_label.configure(text=self.format_time(self.current_time))
            pygame.mixer.stop()
            self.timer_running = True  # makes sure that once clicking okay on the messagebox 
            self.run_timer()           # It goes to the next timer whether work to break vice versa

    def on_closing(self):
        self.timer_running = False
        self.destroy()

if __name__ == "__main__":
    ctk.set_appearance_mode("System")  # Use system appearance mode (dark/light mode)
    ctk.set_default_color_theme("blue")  # Set the default theme color
    app = PomodoroApp()
    app.mainloop()
