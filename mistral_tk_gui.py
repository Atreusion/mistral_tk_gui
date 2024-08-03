"""GUI using tkinter for MistralOrca LLM using GPT4All"""

import time
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import threading
from gpt4all import GPT4All

# the filename of the model, e.g. "mistral-7b-openorca.Q4_0. gguf"
MODEL_NAME = "mistral-7b-openorca.Q5_K_M.gguf"

# the path of where the model file is stored, with escaped backslashes, e.g. "C:\\mistral\\"
MODEL_PATH = "C:\\mistral\\"

# instantiate model with given model file, and do not allow downloading the models from the internet
MODEL = GPT4All(MODEL_NAME, model_path = MODEL_PATH, allow_download = False)

# system_template = "<|im_start|›system\nYou are MistralOrca, a large language model trained" \
#     "by Alignment Lab AI. For multi-step problems, write out your reasoning for each step." \
#     "\n<|im_end|›"  # original system template
# prompt_ template = '<|im_start|›user\n{0}<|im_end|›\n<|im_start|›assistant\n'


class GPTapp:
    """Create the GUI"""

    def __init__(self, root):
        self.generating = False  # flag for whether the program is generating
        self.input_text = tk.StringVar()
        self.tokens = tk.IntVar(value = 200)
        self.temp = tk.DoubleVar(value = 0.7)
        self.time_int = tk.IntVar(value = 1)

        root.title("Mistral + GPTALL")  # set the window title

        # create the main frame
        main_frame = ttk.Frame(root, padding=3)
        main_frame.grid(column=0, row=0, sticky="nesw")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight = 1)

        # bind the return key to start_gen_thread function
        root.bind("<Return>", self.start_gen_thread)

        left_column = ttk.Frame(main_frame)
        left_column.grid_columnconfigure(0, weight = 1)
        left_column.pack(side = 'left', fill = 'both')

        self.output_text_box = ScrolledText(left_column,
                                            wrap = tk.WORD,
                                            width = 100,
                                            height = 20)

        self.output_text_box.grid(column = 0, row = 0, columnspan = 2, pady = (0, 3))

        input_text_box = ttk.Entry(left_column, width=80, textvariable=self.input_text)
        input_text_box.grid(column = 0, row = 1, sticky = 'ew')

        input_button = ttk.Button(left_column, text="Send", command = self.start_gen_thread)
        input_button.grid(column=1, row=1, padx = (3, 0))

        right_column = ttk.Frame(main_frame)
        right_column.pack(side = "right", fill = 'both')

        self.version_label = ttk. Label(right_column, text = "v0.1.20240306", anchor = "w")
        self.version_label.pack(fill = 'x')
        self.version_label.bind("<Button-1>", self.easter_egg)

        tokens_label = ttk.Label(right_column, text = "Tokens (≥1, 200 default):")
        tokens_label.pack(fill = 'x')

        # registers the int_validate function as a callback function, using a Tcl wrapper
        int_validate_cmd = root.register(self.int_validate)
        token_text_box = ttk.Entry(right_column,
                                   width = 6,
                                   textvariable = self.tokens,
                                   validate = 'key',
                                   validatecommand = (int_validate_cmd, "%P", "%d"))
        token_text_box.pack(anchor = 'w')

        temp_label = ttk.Label(right_column, text = "Temp (≥0, 0.7 default):")
        temp_label.pack(fill = 'x')

        # registers the float_validate function as a callback function, using a Tcl wrapper
        float_validate_cmd = root.register(self.float_validate)
        temp_text_box = ttk.Entry(right_column,
                                  width = 6,
                                  textvariable = self.temp,
                                  validate = 'key',
                                  validatecommand = (float_validate_cmd, "%P", "%d"))
        temp_text_box.pack(anchor = 'w')

        time_checkbox = ttk.Checkbutton(right_column,
                                        text = "Show generation time",
                                        variable = self.time_int)

        time_checkbox.pack(anchor = 'w')

        # creates the "Generating..." label, but doesn't show it yet!
        self.generating_label = ttk.Label(right_column, text = "Generating...")

    def easter_egg(self, *args):
        """Easter egg function"""
        self.version_label.config(text = '\U0001F408')

    def gen_func(self, prompt, max_tokens = 200, temp = 0.7):
        """
        Parameters:
        prompt: The user's prompt.

        max_tokens: The number of tokens to generate. See project GitLab for explanation.
        The default is 200.

        temp: The temp of the model response generation. See project GitLab for explanation.
        The default is 0.7.
        """
        output = MODEL.generate(prompt = prompt,
                                max_tokens = max_tokens,
                                temp = temp)  # generate! this is where the magic happens.

        self.generating = False  # set flag showing the program is not generating anymore
        elapsed_time = time.time() - self.start_time
        if output[0] == " ":
            output = output[1:]  # get rid of trailing space at the beginning that sometimes appears
        time_str = f"\n({elapsed_time:.2f} s)" if self.time_int.get() else ""
        output = "AI: \t" + output + time_str + "\n"

        self.output_text_box.insert("end", output)
        self.output_text_box.see("end")
        self.generating_label.pack_forget()  # make the "Generating..." label disappear

    def start_gen_thread(self, *args):
        """Function that sends the gen_func function to it's own thread"""
        prompt = self.input_text.get()
        if len(prompt) > 0 and not self.generating:
            self.start_time = time.time()
            self.generating = True  # set flag showing the program is currently generating
            try:  # try to use the user-defined token value, fallback to 200
                max_tokens = self.tokens.get()
            except ValueError:
                max_tokens = 200
            try:  # try to use the user-defined temperature value, fallback to 0.7
                new_temp = self.temp.get()
            except ValueError:
                new_temp = 0.7
            self.input_text.set("")  # clear the input box
            self.output_text_box.insert("end", "User:\t" + prompt + "\n")
            self.generating_label.pack(anchor = 'w')  # make the "Generating..." label appear
            # send the gen_func function off to it's own thread
            threading.Thread(target = self.gen_func,
                             args = (prompt, max_tokens, new_temp, )).start()

    def int_validate(self, p, d):
        """Validate int input"""
        if d == '1' and not p.isdigit():  # 1 = insert
            return False
        return True

    def float_validate(self, p, d):
        """Validate float input"""
        if d == '1':  # 1 = insert
            try:
                float(p)
                return True
            except ValueError:
                return False
        return True


with MODEL.chat_session():  # this allows the GPT4All model to hold a chat session, with history
    ROOT = tk.Tk()
    GPTapp(ROOT)
    ROOT.mainloop()
