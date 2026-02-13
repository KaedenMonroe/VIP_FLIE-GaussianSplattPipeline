import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from core.pipeline_manager import PipelineManager
from core.category import SelectionMode

class LibraryWidget(tk.Frame):
    """
    Left Sidebar.
    Displays categories and their sections.
    Handles 'Selection' (viewing options) and 'Staging' (adding to pipeline).
    """
    def __init__(self, parent, manager: PipelineManager, on_view_section: Callable):
        super().__init__(parent)
        self.manager = manager
        self.on_view_section = on_view_section # Callback when user clicks name to view options
        
        self._setup_ui()
        # Listen for updates
        self.manager.add_staging_listener(self._refresh_toggles)

    def _setup_ui(self):
        # We use a Canvas+Frame to allow scrolling if list is long
        canvas = tk.Canvas(self, bg='lightgray')
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg='lightgray')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.toggle_vars = {} # Map section.name -> tk.BooleanVar

        category_count = 1
        
        for category in self.manager.categories:
            category_text = str(category_count) + ". " + category.name
            category_count += 1
            # Header
            cat_frame = tk.Frame(self.scrollable_frame, bg='darkgray', pady=2)
            cat_frame.pack(fill='x', pady=2)
            tk.Label(cat_frame, text=category_text, bg='darkgray', font=('Helvetica', 10, 'bold')).pack(anchor='w', padx=5)
            
            # Items
            for section in category.sections:
                row = tk.Frame(self.scrollable_frame, bg='lightgray')
                row.pack(fill='x', padx=10, pady=1)
                
                # Checkbox for Staging
                var = tk.BooleanVar(value=False)
                self.toggle_vars[section.name] = var
                
                # We need to capture 'section' in lambda properly
                cmd = lambda s=section, v=var: self._on_toggle(s, v)
                
                chk = tk.Checkbutton(row, variable=var, command=cmd, bg='lightgray')
                chk.pack(side='left')
                
                # Clickable Label for Viewing
                lbl = tk.Label(row, text=section.name, bg='lightgray', cursor="hand2")
                lbl.pack(side='left', fill='x', expand=True, anchor='w')
                lbl.bind("<Button-1>", lambda e, s=section: self.on_view_section(s))

    def _on_toggle(self, section, var):
        is_staged = var.get()
        self.manager.toggle_section_stage(section, is_staged)
        # Refresh is triggered by callback to handle Single-Select logic automatically updating UI

    def _refresh_toggles(self):
        """Update checkboxes based on actual staged status."""
        for section in self.manager.staged_sections:
            if section.name in self.toggle_vars:
                self.toggle_vars[section.name].set(True)
        
        # Also need to uncheck ones NOT in staged
        staged_names = [s.name for s in self.manager.staged_sections]
        for name, var in self.toggle_vars.items():
            if name not in staged_names:
                var.set(False)

