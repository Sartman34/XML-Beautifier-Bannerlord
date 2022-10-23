import os
import shutil
import sys
import traceback
import tkinter
from tkinter import filedialog
from tkinter import messagebox

from module_directories import directories

class Beautifier():
    def __init__(self, file):
        self.file = file
        self.indent = 0
        
        with open(self.file, "r") as file:
            self.text = file.read()
        whitespace = ["\n", "\t"]
        for char in whitespace:
            self.text = self.text.replace(char, " ")
        lines = [self.raw_line("<" + line) for line in self.text.split("<")[1:]]
        self.text = "\n".join(self.beautify_line(line) for line in lines)

    def raw_line(self, line):
        while " "*2 in line:
            line = line.replace(" "*2, " ")
        to_strip = ["<", ">", "=", "?", "!", "/"]
        stripped_line = []
        part = ""
        for char in line:
            if char in to_strip:
                stripped_line.extend([part.strip(" "), char])
                part = ""
            else:
                part += char
        stripped_line.append(part.strip(" "))
        line = "".join(stripped_line)
        return line

    def newline(self):
        return "\n" + "\t" * self.indent

    def beautify_line(self, line):
        indent_modes = {
            "/>" : "no_indent",
            "<" : "add_indent",
            "</" : "de_indent",
        }
        result = "\t" * self.indent
        i = 0
        newline = False
        define_mode = False
        comma_char = ""
        attribute_mode = False
        indent_mode = "no_indent"
        while i < len(line):
            if newline:
                result += self.newline()
                newline = False
            char = line[i]
            double_chars = ["</", "/>", "<!", "<?"]
            for first, last in double_chars:
                if char == first and i + 1 < len(line) and line[i + 1] == last:
                    char = first + last
                    i += 1
            if char in ["<!", "<?"]:
                define_mode = True
            if char in ["\"", "'"]:
                if not comma_char:
                    comma_char = char
                elif comma_char == char:
                    comma_char = ""
            if char in indent_modes:
                indent_mode = indent_modes[char]
            if char[-1] == ">":
                define_mode = False
            if define_mode or comma_char:
                result += char
            elif char in ["="]:
                result += " " + char + " "
            elif char in [" "]:
                if not attribute_mode:
                    attribute_mode = True
                    self.indent += 1
                result += char
                newline = True
            elif char in [">", "/>"] and attribute_mode:
                self.indent -= 1
                result += self.newline()
                result += char
                newline = True
                attribute_mode = False
            else:
                result += char
            i += 1
        if indent_mode == "add_indent":
            self.indent += 1
        elif indent_mode == "de_indent":
            self.indent -= 1
            result = result[1:]
        result = result.replace("\t", " " * 4)
        return result

    def write(self, directory):
        with open(directories.beautified_file, "w") as file:
            file.write(self.text)

tkinter.Tk().withdraw()
files = tkinter.filedialog.askopenfilenames(title = "Select a File", initialdir = directories.original, filetypes = (("all files", "*.*"),))
if not files:
    messagebox.showerror("Error", "Process canceled.")
    sys.exit()
try:
    for file in files:
        directories.beautified_file.format(basename = os.path.basename(file))
        beautifier = Beautifier(file)
        beautifier.write(directories.beautified_file)
        if messagebox.askyesno("File Complete", "\"{}\" is processed successfuly.\nDo you want to open this file ?".format(directories.beautified_file.basename())):
            os.system(directories.beautified_file.string())
except:
    messagebox.showerror("Error", traceback.format_exc())
    sys.exit()

messagebox.showinfo("Process Successful", "{} file(s) processed successfuly.\nClosing the application...".format(len(files)))
