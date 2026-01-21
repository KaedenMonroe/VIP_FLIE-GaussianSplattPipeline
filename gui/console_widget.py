import tkinter as tk
from tkinter import scrolledtext
import queue

class ConsoleWidget(tk.Frame):
    """
    A unified Output Console.
    Polls a thread-safe Queue to update the text widget.
    """
    def __init__(self, parent: tk.Widget, output_queue: queue.Queue, poll_interval_ms: int = 100):
        super().__init__(parent)
        self.output_queue = output_queue
        self.poll_interval_ms = poll_interval_ms
        
        # UI Setup
        self.text_area = scrolledtext.ScrolledText(self, state='disabled', height=10)
        self.text_area.pack(fill='both', expand=True)
        
        # Start Polling
        self.after(self.poll_interval_ms, self._poll_queue)

    def _poll_queue(self):
        """Checks for new messages in the queue."""
        try:
            while True:
                # Get all available messages (non-blocking)
                text = self.output_queue.get_nowait()
                self._append_text(text)
                self.output_queue.task_done()
        except queue.Empty:
            pass
        finally:
            # Reschedule poll
            self.after(self.poll_interval_ms, self._poll_queue)

    def _append_text(self, text: str):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END) # Auto-scroll
        self.text_area.config(state='disabled')
