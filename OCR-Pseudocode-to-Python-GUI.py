import tkinter as tk
from tkinter import font
import tkinter.scrolledtext as tkst

import subprocess
import sys
import os
import re
import queue
from threading import Thread


keywords = ["GLOBAL", "STR", "INT", "FLOAT", "PRINT", "INPUT", "FOR", \
            "NEXT", "WHILE", "ENDWHILE", "DO", "UNTIL", "AND", "OR", \
            "NOT", "IF", "ELSE", "ELSEIF", "ENDIF", "SWITCH", "CASE", \
            "DEFAULT", "LENGTH", "SUBSTRING", "FUNCTION", "ENDFUNCTION", \
            "PROCEDURE", "ENDPROCEDURE", "ARRAY", "OPENREAD", "OPENWRITE", \
            "ENDOFFILE", "CLOSE"]

def run(cmd):
    global app
    os.environ['PYTHONUNBUFFERED'] = "1"
    #app.main_window.p.stdin.write("print('ben')\n".encode())
    #app.main_window.p.stdin.flush()
    app.main_window.p.stdin.write(cmd.encode())
    #app.main_window.p.stdin.write("print('ben')\n".encode())
    app.main_window.p.stdin.flush()

    '''
    proc = subprocess.Popen(cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT,
    )
    stdout, stderr = proc.communicate()
 '''
    return proc.returncode, stdout, stderr




# Using code from
# https://stackoverflow.com/questions/21811464/how-can-i-embed-a-python-interpreter-frame-in-python-using-tkinter
class Console(tk.Frame):
    main_window = None
    def __init__(self,parent=None):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.createWidgets()

        # get the path to the console.py file assuming it is in the same folder
        consolePath = os.path.join(os.path.dirname(__file__),"console.py")
        # open the console.py file (replace the path to python with the correct one for your system)
        # e.g. it might be "C:\\Python35\\python"
        self.p = subprocess.Popen([sys.executable,consolePath],
                                  stdout=subprocess.PIPE,
                                  stdin=subprocess.PIPE,
                                  stderr=subprocess.PIPE)

        # make queues for keeping stdout and stderr whilst it is transferred between threads
        self.outQueue = queue.Queue()
        self.errQueue = queue.Queue()

        # keep track of where any line that is submitted starts
        self.line_start = 0

        # make the enter key call the self.enter function
        self.ttyText.bind("<Return>",self.enter)

        # a daemon to keep track of the threads so they can stop running
        self.alive = True
        # start the functions that get stdout and stderr in separate threads
        Thread(target=self.readFromProccessOut).start()
        Thread(target=self.readFromProccessErr).start()

        # start the write loop in the main thread
        self.writeLoop()

    def destroy(self):
        "This is the function that is automatically called when the widget is destroyed."
        self.alive=False
        # write exit() to the console in order to stop it running
        self.p.stdin.write("exit()\n".encode())
        self.p.stdin.flush()
        # call the destroy methods to properly destroy widgets
        self.ttyText.destroy()
        tk.Frame.destroy(self)

    def enter(self,e):
        "The <Return> key press handler"
        string = self.ttyText.get(1.0, tk.END)[self.line_start:]
        self.line_start+=len(string)
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
            self.after(10,self.writeLoop)

    def write(self,string):
        self.ttyText.insert(tk.END, string)
        self.ttyText.see(tk.END)
        self.line_start+=len(string)

    def createWidgets(self):
        self.ttyText = tk.Text(self, wrap=tk.WORD)
        self.ttyText.pack(fill=tk.BOTH,expand=True)


class Application(tk.Frame):
    def execute(self, debug=False):
        with open("temp.code","w") as file:
            file.write(self.editor.get("1.0",tk.END))
            
        if debug:
            #code, out, err = run([sys.executable, "OCR-Pseudocode-to-Python.py", "--file=temp.code", "--debug"])
            run("exec(open('OCR-Pseudocode-to-Python.py').read())\n")
        else:
            code, out, err = run([sys.executable, "OCR-Pseudocode-to-Python.py", "--file=temp.code", ])
            
        #print(out)
        self.output.delete("1.0", tk.END)
        self.output.insert("1.0", out)

    def execute_debug(self):
        self.execute(debug=True)
        
    def createWidgets(self):


        self.execute_button = tk.Button(self)
        self.execute_button["text"] = "Execute",
        self.execute_button["command"] = self.execute

        self.execute_button.pack({"side": "left"})

        self.debug_button = tk.Button(self)
        self.debug_button["text"] = "Debug",
        self.debug_button["command"] = self.execute_debug

        self.debug_button.pack({"side": "left"})

        self.QUIT = tk.Button(self)
        self.QUIT["text"] = "Exit"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit

        self.QUIT.pack({"side": "left"})
        
        self.editor = CustomText()

        self.editor.pack({"side":"top"})

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
        self.main_window = Console(root)
        self.main_window.pack(fill=tk.BOTH,expand=True)        
        
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
        tk.Text.__init__(self, *args, **kwargs)
        self.bind("<KeyRelease>", self.OnEntryClick) #keyup
        #keyword_font = font.Font(family="Helvetica",size=36)
        #bold_font.configure(color="red")
        self.tag_configure("keyword", foreground="red")
        self.tag_configure("string", foreground="green") 

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
            index = self.search(pattern, "matchEnd","searchLimit",
                                count=count, regexp=regexp)
            if index == "": break
            if count.get() == 0: break # degenerate pattern which matches zero-length strings
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")
         
    def OnEntryClick(self, event):
        for tag in self.tag_names():
            self.tag_remove(tag, "1.0", "end")        
        self.highlight_pattern(pattern="([[:space:]]|^)("+"|".join(keywords)+")",tag="keyword",regexp=True)
        self.highlight_pattern(pattern="\".*\"",tag="string",regexp=True)
        
root = tk.Tk()
app = Application(master=root)
app.mainloop()
root.destroy()
