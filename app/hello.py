import tkinter as tk
from tkinter import messagebox
t = tk.Tk()
t.title("UIET")
t.config(bg = "Light Blue")
t.geometry("500x500")

menubar = tk.Menu(t)

file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="New")
file_menu.add_command(label="Open")
file_menu.add_command(label="Save")
file_menu.add_separator()
file_menu.add_command(label="logut", command=t.quit)

menubar.add_cascade(label="File", menu=file_menu)

edit_menu = tk.Menu(menubar, tearoff=0)
edit_menu.add_command(label="Cut")
edit_menu.add_command(label="Copy")
edit_menu.add_command(label="Paste")

menubar.add_cascade(label="Edit", menu=edit_menu)

t.config(menu=menubar)


def hh():
    m = p.get()
    n = q.get()
    if (m == "Abhinav" and n == "123"):
        t.quit()
        import menu
    else:
        messagebox.showinfo("Invalid User")

p = tk.StringVar(t)
q = tk.StringVar(t)

l1 = tk.Label(t, text = "Welcome to the UIET Page")
l1.place(x = 10, y =0)

l1 = tk.Label(t, text = "Username")
l1.place(x = 60, y = 20)

e = tk.Entry(textvariable=p)
e.place(x= 150, y = 20)

l1 = tk.Label(t, text = "Password")
l1.place(x = 60, y = 40)

e = tk.Entry(textvariable=q)
e.place(x = 150, y = 40)

b = tk.Button(t, text = "Login", command=hh)
b.place(x = 200, y = 90)

t.mainloop()