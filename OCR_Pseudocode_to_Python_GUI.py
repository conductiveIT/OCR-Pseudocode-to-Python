import tkinter as tk
from tkinter import font, filedialog, messagebox
import tkinter.scrolledtext as tkst

from threading import Thread
import subprocess

import sys
import os

import queue

keywords = ["GLOBAL", "STR", "INT", "FLOAT", "PRINT", "INPUT", "FOR",
            "NEXT", "WHILE", "ENDWHILE", "DO", "UNTIL", "AND", "OR",
            "NOT", "IF", "ELSE", "ELSEIF", "ENDIF", "SWITCH", "CASE",
            "DEFAULT", "LENGTH", "SUBSTRING", "FUNCTION", "ENDFUNCTION",
            "PROCEDURE", "ENDPROCEDURE", "ARRAY", "OPENREAD", "OPENWRITE",
            "ENDOFFILE", "CLOSE", "TO"]


def run(cmd):
    global app
    os.environ['PYTHONUNBUFFERED'] = "1"
    app.main_window.p.stdin.write(cmd.encode())
    app.main_window.p.stdin.flush()


# Using code from
# https://stackoverflow.com/questions/21811464/how-can-i-embed-a-python-interpreter-frame-in-python-using-tkinter
class Console(tk.Frame):

    main_window = None

    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.createWidgets()

        # get the path to the console.py file assuming it is in the same folder
        consolePath = os.path.join(os.path.dirname(__file__), "console.py")
        # open the console.py file
        self.p = subprocess.Popen([sys.executable, consolePath],
                                  stdout=subprocess.PIPE,
                                  stdin=subprocess.PIPE,
                                  stderr=subprocess.PIPE)

        # make queues for keeping stdout and stderr
        # whilst it is transferred between threads
        self.outQueue = queue.Queue()
        self.errQueue = queue.Queue()

        # keep track of where any line that is submitted starts
        self.line_start = 0

        # make the enter key call the self.enter function
        self.ttyText.bind("<Return>", self.enter)

        # a daemon to keep track of the threads so they can stop running
        self.alive = True
        # start the functions that get stdout and stderr in separate threads
        Thread(target=self.readFromProccessOut).start()
        Thread(target=self.readFromProccessErr).start()

        # start the write loop in the main thread
        self.writeLoop()

    def destroy(self):
        "This is the function that is automatically called when the widget is destroyed."
        self.alive = False
        # write exit() to the console in order to stop it running
        self.p.stdin.write("exit()\n".encode())
        self.p.stdin.flush()
        # call the destroy methods to properly destroy widgets
        self.ttyText.destroy()
        tk.Frame.destroy(self)

    def enter(self, e):
        "The <Return> key press handler"
        string = self.ttyText.get(1.0, tk.END)[self.line_start:]
        self.line_start += len(string)
        self.p.stdin.write(string.encode())
        self.p.stdin.flush()

    def readFromProccessOut(self):
        "To be executed in a separate thread to make read non-blocking"
        while self.alive:
            data = self.p.stdout.raw.read(1024).decode()
            self.outQueue.put(data)

    def readFromProccessErr(self):
        "To be executed in a separate thread to make read non-blocking"
        while self.alive:
            data = self.p.stderr.raw.read(1024).decode()
            self.errQueue.put(data)

    def writeLoop(self):
        "Used to write data from stdout and stderr to the Text widget"
        # if there is anything to write from stdout or stderr, then write it
        if not self.errQueue.empty():
            self.write(self.errQueue.get())
        if not self.outQueue.empty():
            self.write(self.outQueue.get())

        # run this method again after 10ms
        if self.alive:
            self.after(10, self.writeLoop)

    def write(self, string):
        self.ttyText.insert(tk.END, string)
        self.ttyText.see(tk.END)
        self.line_start += len(string)

    def createWidgets(self):
        self.ttyText = tkst.ScrolledText(self, wrap=tk.WORD)
        self.ttyText.pack(fill=tk.BOTH, expand=True)


class Application(tk.Frame):
    def about(self):
        messagebox.showinfo("About", "\
OCR Pseudocode IDE\n\n \
Created by conductiveIT\n\n \
Not endorsed by OCR\n\n \
Find out more at: https://github.com/conductiveIT/OCR-Pseudocode-to-Python")

    def execute(self, debug=False):
        with open("temp.code", "w") as file:
            file.write(self.editor.get("1.0", tk.END))

        run("from OCR_Pseudocode_to_Python import *\nload_and_execute_pseudocode('temp.code', "+str(debug)+")\n")

    def execute_debug(self):
        self.execute(debug=True)

    def load(self):
        filename = filedialog.askopenfilename(initialdir="/",
                                title="Select file",
                                filetypes=(("Pseudocode Files", "*.code"), ("All files", "*.*")))
        if (filename != ''):
            try:
                with open(filename) as file:
                    code = file.read()
                    self.editor.delete('1.0', tk.END)
                    self.editor.insert('1.0', code)
                    self.editor.OnEntryClick(None)
            except FileNotFoundError:
                    messagebox.showerror("Error", "File not found")

    def save(self):
        filename = filedialog.asksaveasfilename(initialdir="/",
                        title="Select file",
                        filetypes=(("Pseudocode Files", "*.code"), ("All files", "*.*")))
        with open(filename, "w") as file:
            file.write(self.editor.get('1.0', tk.END))

    def createWidgets(self):
        self.separator = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
        self.separator.pack(fill=tk.X, padx=5, pady=5, )

        self.load_button = tk.Button(self.separator, padx=10)
        self.load_button["text"] = "Load",
        self.load_button["command"] = self.load
        self.load_button.pack({"side": "left"}, padx=10)

        self.save_button = tk.Button(self.separator, padx=10)
        self.save_button["text"] = "Save",
        self.save_button["command"] = self.save
        self.save_button.pack({"side": "left"}, padx=10)

        self.execute_button = tk.Button(self.separator, padx=10)
        self.execute_button["text"] = "Execute",
        self.execute_button["command"] = self.execute

        self.execute_button.pack({"side": "left"}, padx=10)

        self.debug_button = tk.Button(self.separator, padx=10)
        self.debug_button["text"] = "Debug",
        self.debug_button["command"] = self.execute_debug

        self.debug_button.pack({"side": "left"}, padx=10)

        self.about_button = tk.Button(self.separator, padx=10)
        self.about_button["text"] = "About",
        self.about_button["command"] = self.about
        self.about_button.pack({"side": "left"}, padx=10)

        self.quit = tk.Button(self.separator, padx=10)
        self.quit["text"] = "Exit"
        self.quit["fg"] = "red"
        self.quit["command"] = root.destroy

        self.quit.pack({"side": "right"}, padx=10)

        self.label = tk.Label(self.separator, text="Editor")
        self.label.pack()

        self.editor = CustomText(root)
        self.editor.pack({"side": "top"}, fill=tk.BOTH, expand=True)

        '''
        self.output = tk.Text(yscrollcommand=scroll.set)
        scroll = tk.Scrollbar(self.output)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.output.bind("<Key>", lambda e: "break")
        self.output.pack({"side":"bottom"})

        self.output = tkst.ScrolledText()
        self.output.bind("<Key>", lambda e: "break")
        self.output.pack({"side":"bottom"})
        '''

        self.separator3 = tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN)
        self.separator3.pack(fill=tk.X, padx=5, pady=5)

        self.label = tk.Label(self.separator3, text="Output")
        self.label.pack()

        self.main_window = Console(self.separator3)
        self.main_window.pack({"side": "bottom"}, fill=tk.BOTH, expand=True)

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()


class CustomText(tk.Text):
    '''A text widget with a new method, highlight_pattern()

    example:

    text = CustomText()
    text.tag_configure("red", foreground="#ff0000")
    text.highlight_pattern("this should be red", "red")

    The highlight_pattern method is a simplified python
    version of the tcl code at http://wiki.tcl.tk/3246
    '''
    def __init__(self, *args, **kwargs):
        tkst.ScrolledText.__init__(self, *args, **kwargs)
        self.bind("<KeyRelease>", self.OnEntryClick)  # keyup
        self.tag_configure("keyword", foreground="orange")
        self.tag_configure("string", foreground="green")
        self.tag_configure("comment", foreground="red")

    def highlight_pattern(self, pattern, tag, start="0.0", end="end",
                          regexp=False):
        '''Apply the given tag to all text that matches the given pattern

        If 'regexp' is set to True, pattern will be treated as a regular
        expression according to Tcl's regular expression syntax.
        '''

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd", "searchLimit",
                                count=count, regexp=regexp)
            if index == "":
                break
            # degenerate pattern which matches zero-length strings
            if count.get() == 0:
                break
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")

    def OnEntryClick(self, event):
        # Removed all the existing tags
        for tag in self.tag_names():
            self.tag_remove(tag, "1.0", "end")

        # Highlight the keywords
        self.highlight_pattern(pattern="([[:space:]]|^)("+"|".join(keywords)+")",
                               tag="keyword", regexp=True)
        # Highlight any strings
        self.highlight_pattern(pattern="\".*\"", tag="string", regexp=True)
        # Highlight any comments
        self.highlight_pattern(pattern='.*#.*$', tag="comment", regexp=True)

root = tk.Tk()
root.title("OCR Pseudocode IDE")
root.iconbitmap("favicon.ico")
app = Application(master=root)
app.mainloop()
root.destroy()
