import tkinter as tk
from core.pipeline_manager import PipelineManager

class PreviewWidget(tk.Frame):
    """
    Right Sidebar.
    Shows the 'Staged' pipeline sequence.
    Allows reordering.
    """
    def __init__(self, parent, manager: PipelineManager):
        super().__init__(parent)
        self.manager = manager
        
        self._setup_ui()

    def _setup_ui(self):
        tk.Label(self, text="Pipeline Preview", font=("Helvetica", 12, "bold")).pack(pady=5)
        
        self.listbox = tk.Listbox(self, bg="#f0f0f0", selectmode=tk.SINGLE)
        self.listbox.pack(side="top", fill="both", expand=True, padx=5)
        
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill='x', pady=5)
        
        tk.Button(btn_frame, text="▲", command=self._move_up).pack(side='left', padx=5, expand=True)
        tk.Button(btn_frame, text="▼", command=self._move_down).pack(side='left', padx=5, expand=True)
        
        self.warning_lbl = tk.Label(self, text="", fg="red", wraplength=180)
        self.warning_lbl.pack(pady=5)

        # Bottom Status
        self.path_status_lbl = tk.Label(self, text="Paths Missing", fg="red", font=("Helvetica", 10))
        self.path_status_lbl.pack(side='bottom', pady=10)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        last_stage_index = -1
        has_warning = False
        
        for idx, section in enumerate(self.manager.staged_sections):
            cat = self.manager.get_category_of_section(section)
            cat_name = cat.name if cat else "?"
            
            # Simple Display
            self.listbox.insert(tk.END, f"{idx+1}. [{cat_name}] {section.name}")
            
        # Update Path Status
        ctx = self.manager.config.global_context
        if ctx.input_dir and ctx.output_dir:
            self.path_status_lbl.config(text="Paths Configured", fg="green")
        else:
            self.path_status_lbl.config(text="Paths Missing", fg="red")
            
    def _move_up(self):
        sel = self.listbox.curselection()
        if sel:
            idx = sel[0]
            if self.manager.move_staged_item(idx, -1):
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(idx - 1)

    def _move_down(self):
        sel = self.listbox.curselection()
        if sel:
            idx = sel[0]
            if self.manager.move_staged_item(idx, 1):
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(idx + 1)
