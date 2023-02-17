import tkinter as tk
import subprocess
import tkinter.font as font


def onclick():
	subprocess.call("login_sonicwall.py", shell=True)

def onclick2():
	quit()

# create, name and specify size of the window	

window = tk.Tk()
window.title("Wifi Login")
window.geometry("400x200")

# Change Button text 

myFont = font.Font(family="georgia", size="35")

btn = tk.Button(text="Login To Wifi", bg="lightblue", fg="black", font=myFont, command=onclick)
btn2 = tk.Button(text="Exit", bg="firebrick1", font=myFont, command=onclick2)
btn.pack()
btn2.pack()

window.mainloop()