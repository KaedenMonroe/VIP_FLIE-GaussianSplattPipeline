import tkinter as tk
from sections.base_section import PipelineSection

class SectionFrame(tk.Frame):
    """
    The 'View' for a specific PipelineSection.
    It simply calls `section.render_options(self)`.
    """
    def __init__(self, parent: tk.Widget, section: PipelineSection):
        super().__init__(parent)
        self.section = section
        
        # Title of the section (optional visual header)
        header = tk.Label(self, text=f"Configure: {section.name}", font=("Helvetica", 14, "bold"))
        header.pack(pady=(0, 10))
        
        # Render the specific widgets for this section
        self.section.render_options(self)
