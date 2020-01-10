"""
Mental Arithmetic Trainer by Bani Tariveh, github.com/BaniTar
This program is a randomized mental calculation trainer.
The user can set it to show randomized calculations with the settings chosen.
Information about how its settings work can be found under help_message().

The program is kept in a single file to keep it as an easy drag-and-drop.
"""


from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
from random import randint


# Parameters for the program. Can be changed.
MAX_NUMBERS = 5
OPERATORS = ['+', '-', '·']  # List of possible operator marks.
RANGE_LIMIT = 1000
MAX_TIME_LIMIT = 900
CFG_FILE = str(Path(__file__).parent.absolute()) + '/MAT.cfg'
# Tk event key symbols: http://www.tcl.tk/man/tcl8.4/TkCmd/keysyms.htm
SUBMIT_KEY = '<Return>'  # Key for submitting the player's answer.
CLEAR_KEY = '<Next>'  # Key for quickly clearing the field.


# Default entries for user input fields. If config file doesn't exist or is
# faulty, settings will be taken from this dict.
defaults = {
    'numbercount': 2,
    'range_lower': 0,
    'range_upper': 20,
    'operator': OPERATORS[0],
    'time_limit': 120
}


class ArithmeticProgram:
    def __init__(self):
        """
        Creating all the UI elements, setting variables needed for later.
        """
        self.__window = tk.Tk()
        self.__window.title("Mental Arithmetic Trainer")

        # Creating variables for later.
        self.__settings = read_cfg().copy()  # Load saved settings.
        self.__answers_correct = 0
        self.__answers_all = 0
        self.__stoptimer = False
        time_width = 1 + len(str(MAX_TIME_LIMIT))  # space for showing time
        # Control variables for updating.
        self.__results_cur = tk.StringVar(value="")
        self.__results_prev = tk.StringVar(value="")
        self.__time_left = tk.StringVar(value=0)
        launch_numbercount = tk.IntVar(value=self.__settings['numbercount'])

        # Exterior frame used for padding.
        self.__cont_frame = tk.Frame(self.__window, padx=10, pady=10)
        self.__cont_frame.grid(sticky=tk.E+tk.W+tk.N+tk.S)

        # Frame for top part (settings)
        self.__tframe = tk.LabelFrame(self.__cont_frame, text="Settings",
                                      pady=10)
        # Dropdown for how number count. Wrapper frame.
        self.__num_c_wrapper = tk.Frame(self.__tframe, padx=5)

        self.__number_label = tk.Label(self.__num_c_wrapper, text="Numbers")
        self.__numbercount = tk.Spinbox(self.__num_c_wrapper, from_=2,
                                        to=MAX_NUMBERS, width=3,
                                        textvariable=launch_numbercount)

        # Grid numbercount frame and contents
        self.__number_label.grid(row=0, column=0)
        self.__numbercount.grid(row=1, column=0)
        self.__num_c_wrapper.grid(row=0, column=0, sticky=tk.N)

        # (wrapper), set ranges for random numbers.
        self.__range_wrapper = tk.Frame(self.__tframe, padx=5)

        self.__range_label = tk.Label(self.__range_wrapper, text="Range",
                                      padx=5)
        self.__range_lower = tk.Entry(self.__range_wrapper, width=6,
                                      justify=tk.RIGHT)
        self.__range_lower.insert(0, self.__settings['range_lower'])  # Default
        self.__txline = tk.Label(self.__range_wrapper, text="-")
        self.__range_upper = tk.Entry(self.__range_wrapper, width=6)
        self.__range_upper.insert(0, self.__settings['range_upper'])  # Default

        # Grid range frame and contents
        self.__range_label.grid(row=0, column=0, columnspan=3)
        self.__range_lower.grid(row=1, column=0)
        self.__txline.grid(row=1, column=1)
        self.__range_upper.grid(row=1, column=2)
        self.__range_wrapper.grid(row=0, column=1, sticky=tk.N)

        # Operator dropdown menu. (wrapper)
        self.__op_wrapper = tk.Frame(self.__tframe, padx=5)

        self.__op_label = tk.Label(self.__op_wrapper, text="Operator")
        # Dropdown menu for operators.
        self.__op_dropdown = ttk.Combobox(self.__op_wrapper, values=OPERATORS,
                                          width=3)
        self.__op_dropdown.insert(0, self.__settings['operator'])  # Default

        # Grid operator frame and contents.
        self.__op_label.grid(row=0, column=0)
        self.__op_dropdown.grid(row=1, column=0)
        self.__op_wrapper.grid(row=0, column=2, sticky=tk.N)

        # Time limit entry (wrapper)
        self.__time_wrapper = tk.Frame(self.__tframe, padx=5)

        self.__time_label = tk.Label(self.__time_wrapper, text="Time limit")
        self.__time_entry = tk.Entry(self.__time_wrapper, width=time_width,
                                     justify=tk.CENTER)
        self.__time_entry.insert(0, self.__settings['time_limit'])  # Default

        # Grid time wrapper and contents
        self.__time_label.grid(row=0, column=0)
        self.__time_entry.grid(row=1, column=0)
        self.__time_wrapper.grid(row=0, column=3, sticky=tk.N)

        self.__tframe.grid(row=0, column=0, sticky=tk.EW)

        # Middle frame for buttons and timer
        self.__mframe = tk.Frame(self.__cont_frame)

        # Buttons and timer.
        self.__start_button = tk.Button(self.__mframe, width=7, text="Start",
                                        command=self.start_game)
        self.__stop_button = tk.Button(self.__mframe, width=7, text="Stop",
                                       command=self.stop_game)
        self.__help_button = tk.Button(self.__mframe, width=7, text="Help",
                                       command=help_message)
        self.__quit_button = tk.Button(self.__mframe, width=7, text="Quit",
                                       command=self.quit)
        self.__timer_label = tk.Label(self.__mframe, text="Time left:")
        # Timer updates as IntVar timer is updated.
        self.__timer = tk.Label(self.__mframe, height=3, width=time_width,
                                textvariable=self.__time_left)

        # Grid buttons and their frame.
        self.__start_button.grid(row=0, column=0, padx=3)
        self.__stop_button.grid(row=0, column=1, padx=3)
        self.__help_button.grid(row=0, column=2, padx=3)
        self.__quit_button.grid(row=0, column=3, padx=3)
        self.__timer_label.grid(row=0, column=4, padx=3)
        self.__timer.grid(row=0, column=5)
        self.__mframe.grid(row=1, column=0, sticky=tk.EW)

        # Equation frame.
        self.__eqframe = tk.LabelFrame(self.__cont_frame, text="Calculation",
                                       pady=5)
        # Placeholder label so height isn't lost when hiding other elements.
        self.__pholder = tk.Label(self.__eqframe, text="")
        # Left side of the equation.
        self.__eqleft = tk.Frame(self.__eqframe, height=3)
        # Right side, user answer.
        self.__uanswer = tk.Entry(self.__eqframe, width=10)
        # Pressing SUBMIT_KEY initiates answer checking when entry is focused.
        self.__uanswer.bind(SUBMIT_KEY, (lambda event: self.answer_process(
            self.__uanswer.get())))
        # Pressing CLEAR_KEY clears the field.
        self.__uanswer.bind(CLEAR_KEY, lambda event:
                            clear_field(self.__uanswer))

        # Grid equation frame and contents.
        self.__pholder.grid(row=0, column=0)
        self.__eqleft.grid(row=0, column=1, padx=5, sticky=tk.E)
        self.__uanswer.grid(row=0, column=2, sticky=tk.E)
        self.__eqframe.grid(row=2, column=0, ipadx=5, sticky=tk.E+tk.W)

        # Bottom frame for results.
        self.__bframe = tk.LabelFrame(self.__cont_frame, text="Results",
                                      padx=10, pady=5)
        self.__cur_frame = tk.LabelFrame(self.__bframe, text="Current")
        self.__results_label_current = tk.Label(self.__cur_frame, padx=5,
                                        textvariable=self.__results_cur)
        self.__prev_frame = tk.LabelFrame(self.__bframe, text="Previous")
        self.__results_label_previous = tk.Label(self.__prev_frame, padx=5,
                                        textvariable=self.__results_prev)

        # Grid bottom frame stuff.
        self.__cur_frame.grid(row=0, column=0)
        self.__results_label_current.grid()
        self.__prev_frame.grid(row=0, column=1)
        self.__results_label_previous.grid()
        self.__bframe.grid(sticky=tk.EW)

        # Lists for which widgets are active in which game states.
        self.__running_active_widgets = [
            self.__timer_label,
            self.__timer,
            self.__stop_button,
            self.__uanswer
        ]
        self.__stopped_active_widgets = [
            self.__number_label,
            self.__range_label,
            self.__op_label,
            self.__time_label,
            self.__numbercount,
            self.__range_lower,
            self.__range_upper,
            self.__op_dropdown,
            self.__time_entry,
            self.__start_button,
            self.__help_button,
        ]

        # Create eq left side, get all the labels.
        self.create_left_eq()

        # Disable the right elements at launch.
        for i in self.__running_active_widgets:
            i.configure(state=tk.DISABLED)

    def create_left_eq(self):
        """
        Creates all labels required to display the equation in its biggest 
        form. Creates new variables for later use.
        self.__operator: Simply loads the default operator. Needed later.
        self.__numbers: Control variables for label values.
        self.__eq_labels: All labels in a list. Necessary portions of it are
                            unhidden when needed.
        ---This function is run inside init.
        """
        # Control variable so operator label auto-updates.
        self.__operator = tk.StringVar(value=self.__settings['operator'])

        # Creating control variables for label numbers and adding to list.
        # Assignment can be done with for loops, but I wanted to try this out.
        self.__numbers = []
        for i in range(MAX_NUMBERS):
            num = tk.IntVar(value=0)
            self.__numbers.append(num)

        # Create list of number and operator labels. Assign label to
        # corresponding number control variable.
        self.__eq_labels = []
        # Getting the width needed so there is no weird resizing later.
        for i in range(MAX_NUMBERS):
            self.__eq_labels.append(tk.Label(self.__eqleft,
                                             textvariable=self.__numbers[i]))
            # Check if last number before adding operator label.
            # Last label is '='
            if i == MAX_NUMBERS - 1:
                self.__eq_labels.append(tk.Label(self.__eqleft, text="="))

            else:
                self.__eq_labels.append(tk.Label(self.__eqleft,
                                                 textvariable=self.__operator))

        # Grid and hide the labels so they can later be drawn with just grid()
        # and no settings. Add to active when running widgets list.
        for i in range(len(self.__eq_labels)):
            self.__running_active_widgets.append(self.__eq_labels[i])
            self.__eq_labels[i].grid(row=0, column=i)
            self.__eq_labels[i].grid_remove()

        # Enable the right labels at launch with default settings.
        self.left_eq_config()

    def start_game(self):
        """
        Run when the start button is pressed. Validates everything, sets up
        start conditions/settings and starts the game.
        There is no loop in the game, 'turns' are advanced via key press.
        """
        # If push_settings returns True (settings set without error), prepare
        # for game by switchin on elements and compiling variables for game.
        if self.push_settings():
            self.start_game_setup()

            # Starting timer.
            # If limit = 0 -> no timer.
            if self.__settings['time_limit'] != 0:
                self.countdown(self.__settings['time_limit'])

            self.__uanswer.focus()  # Player doesn't have to focus manually.
            # Game has now started and will stop once stopping conditions have
            # been met.

        else:
            return  # Exit start if errors.

    def push_settings(self, display_errors=True):
        """
        Attempts to set settings. 
        :param display_errors: bool to decide to display errors or not.
        :return: T/F based on if settings were successfully planted.
        """
        # Getting all settings.
        temp_settings = {
            'numbercount': self.__numbercount.get(),
            'range_lower': self.__range_lower.get(),
            'range_upper': self.__range_upper.get(),
            'operator': self.__op_dropdown.get(),
            'time_limit': self.__time_entry.get()
        }

        # Validating settings and getting a list of error messages.
        errors, temp__settings = settings_errors(temp_settings)

        # If no errors, prepare for game by switchign on elements and compiling
        # settings for game
        if not errors:
            self.__settings = temp__settings
            return True

        elif display_errors:
            error_message = "The following errors were found:\n\n" + \
                            "\n\n".join(errors)
            showerror("Input error", error_message)
            return False  # Exit start if errors.

        else:
            return False

    def start_game_setup(self):
        """
        Setting up all the variables/ui elements and equation for a new game.
        """
        # Set up left side of the equation based on settings.
        self.left_eq_config()

        # Disable/enable needed buttons/labels.
        for i in self.__stopped_active_widgets:
            i.configure(state=tk.DISABLED)

        for i in self.__running_active_widgets:
            i.configure(state=tk.NORMAL)

        # Set up last variables for game.
        # List of numbers in use. Used by answer process.
        first_used_number_index = MAX_NUMBERS - self.__settings['numbercount']
        self.__numbers_in_use = self.__numbers[first_used_number_index:]

        self.__stoptimer = False  # Reset from previous use.

        # Transfer results to previous and clear current result if last game
        # had any results.
        if self.__results_cur.get() != "":
            self.__results_prev.set(self.__results_cur.get())
            self.__results_cur.set("")

        self.set_new_calculation()

    def left_eq_config(self):
        """
        Sets up the left side of the equation. Needed parts of self.__eq_labels
        are added to GUI.
        """
        numcount = self.__settings['numbercount']  # Amount of numbers used.
        number_label_width = len(str(self.__settings['range_upper'])) + 1
        # Set new operator.
        self.__operator.set(self.__settings['operator'])

        # Clean up all labels from previous game.
        for i in self.__eq_labels:
            i.grid_remove()

        first_used_label_index = len(self.__eq_labels) - numcount * 2
        # Apply width to labels in use.
        for i in range(first_used_label_index, MAX_NUMBERS*2 - 1, 2):
            self.__eq_labels[i].configure(width=number_label_width)
        # Grid the labels that are in use.
        for i in range(first_used_label_index, MAX_NUMBERS*2):
            self.__eq_labels[i].grid()

    def countdown(self, count):
        """
        Countdown timer. Only run if time limit > 0.
        :param count: time until shutdown
        """
        # Stop timer if stop button has been pressed.
        if self.__stoptimer:
            return

        elif count > 0:
            self.__time_left.set(count-1)
            self.__window.after(1000, self.countdown, count - 1)

        # Stop game if time has run out.
        else:
            self.stop_game()
            return

    def answer_process(self, uanswer):
        """
        Processes answer and advances turn accordingly.
        :param uanswer: user answer
        """
        # Get all the numbers from Vars and correct answer.
        numbers = []
        for i in self.__numbers_in_use:
            numbers.append(i.get())

        answer = get_answer(numbers, self.__settings['operator'])

        # Process user answer.
        try:
            if int(uanswer) == answer:
                self.advance_turn(True)

            else:  # Skip if wrong answer.
                self.advance_turn(False)

        except ValueError:
            if uanswer == "":  # Empty used for skipping.
                self.advance_turn(False)

            else:  # Wipe input and give a chance.
                clear_field(self.__uanswer)
                showerror("Bad input", "Input can only be an integer or empty")
            return

    def advance_turn(self, correct):
        """
        Does all the things needed to advance into showing the next equation.
        :param correct: boolean; answer is correct/not.
        """
        self.__answers_all += 1

        if correct:
            self.__answers_correct += 1

        # Update the current results label.
        self.__results_cur.set("%s / %s" %
                               (self.__answers_correct, self.__answers_all))

        self.set_new_calculation()  # New numbers and entry.

    def set_new_calculation(self):
        """
        When initiating game or a new turn, creates a new calculation to show.
        """
        # Set low and high bounds for number generator.
        low = self.__settings['range_lower']
        high = self.__settings['range_upper']

        # Get a random number and update it into the IntVar/label.
        for i in self.__numbers_in_use:
            random_number = randint(low, high)
            i.set(random_number)

        clear_field(self.__uanswer)  # Cleanup input.

    def stop_game(self):
        """
        Run when the stop button is pressed. Stop timer and disables/enables
        buttons for not in game state.
        """
        self.__stoptimer = True  # Stops timer on next countdown.
        self.__time_left.set(0)
        self.__tframe.focus()  # Take away forcus from entry. No more inputs.
        # This is needed even though set_new_calculation() already has it:
        # That f() can't run on a disabled entry, so it doesn't work at start.
        clear_field(self.__uanswer)
        # Disable/enable/grey out needed elements for stopped game.
        for i in self.__running_active_widgets:
            i.configure(state=tk.DISABLED)

        for i in self.__stopped_active_widgets:
            i.configure(state=tk.NORMAL)

        # Game stopped.

        # Flush answer counts.
        self.__answers_correct = 0
        self.__answers_all = 0

    def start(self):
        self.__window.mainloop()

    def quit(self):
        """
        Attempt to save settings and quit.
        """
        self.push_settings(display_errors=False)
        write_cfg(self.__settings)
        self.__window.destroy()


def settings_errors(s):
    """
    Validates and processes settings, creates error messeages.
    :param s: dict of settings.
    :return: error messages, processed settings.
    """
    error_messages = []
    # Check for integer-only input. This has to be checked first before
    # messages for other errors can be sent. Check will return immediately.
    for i in s:
        if i != 'operator':  # Need to int() all except operator.
            try:
                s[i] = int(s[i])
            except ValueError:
                error_messages.append("All input fields except operator must "
                                      "only contain integers.")
                return error_messages, s

    # Valid numcount.
    if not 1 < s['numbercount'] <= MAX_NUMBERS:
        error_messages.append("Number settings: maximum amount of numbers "
                              "allowed in the calculation is %s."
                              % MAX_NUMBERS)

    # If ranges out of... range.
    if not 0 <= s['range_lower'] <= RANGE_LIMIT or \
            not 0 <= s['range_upper'] <= RANGE_LIMIT:
        error_messages.append("Range settings: allowed range for the numbers "
                              "is from %s to %s."
                              % (0, RANGE_LIMIT))

    # Lower range bigger than upper.
    if s['range_lower'] >= s['range_upper']:
        error_messages.append("Range settings: lower range must be smaller "
                              "than upper range.")

    # Operator doesn't exist.
    if s['operator'] not in OPERATORS:
        error_messages.append("Operator: unsupported operator, choose one from"
                              " dropdown list.")

    # Invalid time input
    if not -1 < s['time_limit'] < MAX_TIME_LIMIT:
        error_messages.append("Time limit: must be between 0 and %s." %
                              MAX_TIME_LIMIT)

    return error_messages, s


def get_answer(numbers, op):
    """
    Based on chosen operator, do operation to find out correct answer.
    :param numbers: list of numbers
    :param op: operator
    :return: correct answer
    """

    # Addition.
    if op == "+":
        answer = sum(numbers)
        return answer

    # Subtraction.
    elif op == "-":
        base = numbers[0]
        for i in numbers[1:]:
            base -= i
        answer = base
        return answer

    # Multiplication
    elif op == "·":
        base = numbers[0]
        for i in numbers[1:]:
            base *= i
        answer = base
        return answer

    else:
        showerror("No", "This really shouldn't happen. Bug report time.")
        return 0


def clear_field(field):
    """
    Clears answer input field when keyboard button is pressed.
    :param field: the text field object
    """
    field.delete(0, tk.END)


def help_message():
    """
    Help message.
    """
    showinfo(
        "Help",
        "This program is for training mental arithmetic.\n\n"
        "The numbers setting lets you change how many numbers will be in "
        "the calculation. (2-%s)\n\n"
        "The range setting lets you choose the range in which the"
        "numbers are randomly chosen from. (0-%s)\n\n"
        "The operator setting will let you choose the calculation method.\n\n"
        "Time limit: you can set a timer. If it is set to 0, timer will be"
        " disabled. (0-%s)\n\n"
        "When the game is started, simply write the correct answer and "
        "press the ENTER button to submit it and move on to the next one."
        " The game will run until you press start or until timer runs out."
        " Pressing ENTER when the answer box is empty will skip.\n\n"
        "Your current and previous scores will be shown in the bottom."
        % (MAX_NUMBERS, RANGE_LIMIT, MAX_TIME_LIMIT)
    )


def write_cfg(settings):
    """
    Create new config file from provided settings.
    :param settings: program settings dict
    """
    newfile = open(CFG_FILE, 'w')
    lines = []

    for i in settings:
        line_words = [i, str(settings[i])]
        line = ";".join(line_words)
        lines.append(line)

    filetext = "\n".join(lines)
    newfile.write(filetext)
    newfile.close()


def read_cfg():
    """
    Reads the settings from file into program. Reset config file if any error
    occurs during reading & processing.
    :return: settings
    """
    try:
        confile = open(CFG_FILE, 'r')
        lines = confile.readlines()
        confile.close()
        temp_settings = {}

        for i in lines:
            line = i.rstrip()
            words = line.split(';')
            setting = words[0]
            value = words[1]

            if setting != 'operator':
                temp_settings[setting] = int(value)

            else:
                temp_settings[setting] = value

        for i in defaults:
            if i not in temp_settings:  # All settings must be present.
                raise ValueError

        return temp_settings

    except IndexError:
        write_cfg(defaults)
        showerror("File error", "The configuration file is faulty.\n"
                                "Creating a new default file.")
        return defaults

    except ValueError:
        showerror("File error", "The configuration file is faulty.\n"
                                "Creating a new default file.")
        write_cfg(defaults)
        return defaults

    except OSError:  # Create new cfg if no file.
        showerror("File error", "The configuration file was not found or could"
                                " not be accessed. A new one will be created. "
                                "\nIf this is the first time you're launching"
                                "the program, this is supposed to happen.")
        write_cfg(defaults)
        return defaults


def main():
    ui = ArithmeticProgram()
    ui.start()


main()
