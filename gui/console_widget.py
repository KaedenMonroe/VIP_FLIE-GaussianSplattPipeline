import tkinter as tk
from tkinter import scrolledtext
import queue
from .style import consoleColor, toolbarColor, normalTextColor, consoleError, consoleNormal, consoleWarning

class ConsoleWidget(tk.Frame):
    """
    A unified Output Console.
    Polls a thread-safe Queue to update the text widget.
    """
    def __init__(self, parent: tk.Widget, output_queue: queue.Queue, poll_interval_ms: int = 100):
        super().__init__(parent)
        self.configure(background=consoleColor)
        self.output_queue = output_queue
        self.poll_interval_ms = poll_interval_ms
        self.current_text_column = 1
        
        # UI Setup
        self.text_area = scrolledtext.ScrolledText(self, state='disabled', height=10, 
                                                   background=consoleColor, foreground=normalTextColor)
        #TODO: Fix scrollbar coloring
        #self.text_area.vbar.configure(troughcolor=consoleScrollcolor)
        self.text_area.tag_config("Manager Error", foreground=consoleError)
        self.text_area.tag_config("Manager Warning", foreground=consoleWarning)
        self.text_area.tag_config("Manager", foreground=consoleNormal)

        self.text_area.pack(fill='both', expand=True)
        
        # Start Polling
        self.after(self.poll_interval_ms, self._poll_queue)

    def _poll_queue(self):
        """Checks for new messages in the queue."""
        try:
            while True:
                # Get all available messages (non-blocking)
                text = self.output_queue.get_nowait()
                self._append_text(text, self.text_area)
                self.output_queue.task_done()
        except queue.Empty:
            pass
        finally:
            # Reschedule poll
            self.after(self.poll_interval_ms, self._poll_queue)

    def _append_text(self, text: str, text_area):
        text_area.config(state='normal')
        text_split = text.splitlines(keepends=False)
        # print(text_area)
        for line in text_split:
            if line:
                text_area.insert(tk.END, line +"\n")
                if '[Manager Error]:' in line:
                    index = line.find('[Manager Error]:')
                    text_area.tag_add("Manager Error", 
                                        str(self.current_text_column)+'.'+str(index),
                                        str(self.current_text_column)+'.'+str(index+16))
                if '[Manager WARNING]:' in text:
                    index = text.find('[Manager WARNING]:')
                    self.text_area.tag_add("Manager Warning", 
                                           float(str(self.current_text_column)+'.'+str(index)),
                                           float(str(self.current_text_column)+'.'+str(index+18)))
                if '[Manager]:' in line:
                    index = line.find('[Manager]:')
                    self.text_area.tag_add("Manager", 
                                           str(self.current_text_column)+'.'+ str(index),
                                           str(self.current_text_column)+'.'+ str(index+10))
                if '[System]:' in line:
                    index = line.find('[System]:')
                    self.text_area.tag_add("Manager", 
                                           str(self.current_text_column)+'.'+ str(index),
                                           str(self.current_text_column)+'.'+ str(index+9))
                self.current_text_column += 1
        
            
        
        self.text_area.see(tk.END) # Auto-scroll
        
        self.text_area.config(state='disabled')
       
    