"""
Provides a space to manualy change the UI theme 
TODO custom theme support via json
"""
import tkinter as tk

bgColor = '#232528'
toolbarColor = '#2F3237'
buttonHoverColor = '#383C42'
sectionColor = '#383C42'
normalTextColor = '#EEEEEE'
sectionBorderColor = '#3DAFE0'
consoleColor = '#2F3237'
consoleScrollcolor = '#383C42'
debug = '#39FF14'

class Stylemanager():
    def __init__(self):
        pass
    
    def styleMain(self, tkobject):
        tkobject.configure(background=bgColor)

    def styleSection(self, tkobject):
        tkobject.configure(background=bgColor)
            
    def styleToolbar(self, tkobject):
        tkobject.configure(background=toolbarColor)
        
    def styleButton(self, tkobject):
        tkobject.configure(background=toolbarColor, foreground=normalTextColor, font=("Consolas", 10))