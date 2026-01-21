import tkinter as tk
from tkinter import filedialog, ttk
import os

from core.pipeline_manager import PipelineConfiguration

class PathSelectionWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk, config: PipelineConfiguration):
        super().__init__(parent)
        self.title("Select I/O Paths")
        self.geometry("600x500")
        
        self.config = config
        self.on_update = None # Callback function
        
        self._setup_ui()
        
        # Populate initial values
        self._refresh_ui_from_config()

    def set_callback(self, callback):
        self.on_update = callback

    def _setup_ui(self):
        # Input Dir
        frame_in = tk.LabelFrame(self, text="Input Directory (Start)", padx=10, pady=10)
        frame_in.pack(fill='x', padx=10, pady=5)
        
        self.var_input = tk.StringVar()
        tk.Entry(frame_in, textvariable=self.var_input, state='readonly').pack(fill='x', side='left', expand=True, padx=5)
        tk.Button(frame_in, text="Select...", command=self._select_input).pack(side='right', padx=2)
        tk.Button(frame_in, text="Clear", command=self._clear_input).pack(side='right', padx=2)

        # Output Dir
        frame_out = tk.LabelFrame(self, text="Output Directory (Final)", padx=10, pady=10)
        frame_out.pack(fill='x', padx=10, pady=5)
        
        self.var_output = tk.StringVar()
        tk.Entry(frame_out, textvariable=self.var_output, state='readonly').pack(fill='x', side='left', expand=True, padx=5)
        tk.Button(frame_out, text="Select...", command=self._select_output).pack(side='right', padx=2)
        tk.Button(frame_out, text="Clear", command=self._clear_output).pack(side='right', padx=2)

        # Confirm Button
        tk.Button(self, text="Confirm Selection", command=self.destroy, bg="#dddddd").pack(side='bottom', pady=10)

        # File List Preview
        preview_frame = tk.LabelFrame(self, text="Input Directory Contents", padx=10, pady=10)
        preview_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview for file list
        self.tree = ttk.Treeview(preview_frame, columns=("size",), show='headings')
        self.tree.heading("size", text="Size")
        self.tree.column("size", width=100, anchor='e')
        # We need a primary column for filename, which Treeview has by default as '#0' if show='tree', 
        # but here we use display columns. Let's make column #0 be the Name.
        # Actually standard Treeview usage: column #0 is the tree node. 
        # Let's switch to show='tree headings' or just columns map.
        # Simpler: One column for Name (tree column) and one for Size.
        
        self.tree = ttk.Treeview(preview_frame, columns=("size",), selectmode='none')
        self.tree.heading("#0", text="Name", anchor='w')
        self.tree.heading("size", text="Size", anchor='e')
        self.tree.column("#0", anchor='w')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')


    def _refresh_ui_from_config(self):
        ctx = self.config.global_context
        self.var_input.set(ctx.input_dir)
        self.var_output.set(ctx.output_dir)
        
        self._populate_file_list(ctx.input_dir)

    def _select_input(self):
        path = filedialog.askdirectory(title="Select Input Directory")
        if path:
            self.config.global_context.input_dir = path
            self._refresh_ui_from_config()
            if self.on_update: self.on_update()

    def _clear_input(self):
        self.config.global_context.input_dir = ""
        self._refresh_ui_from_config()
        if self.on_update: self.on_update()

    def _select_output(self):
        path = filedialog.askdirectory(title="Select Output Directory")
        if path:
            self.config.global_context.output_dir = path
            self._refresh_ui_from_config()
            if self.on_update: self.on_update()

    def _clear_output(self):
        self.config.global_context.output_dir = ""
        self._refresh_ui_from_config()
        if self.on_update: self.on_update()

    def _populate_file_list(self, folder_path):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not folder_path or not os.path.exists(folder_path):
            return

        try:
            # Simple non-recursive listing
            for entry in os.scandir(folder_path):
                # Basic info
                name = entry.name
                size_str = ""
                if entry.is_file():
                    size = entry.stat().st_size
                    # formatting size
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size/1024:.1f} KB"
                    else:
                        size_str = f"{size/(1024*1024):.1f} MB"
                elif entry.is_dir():
                    size_str = "<DIR>"
                
                # Insert
                # We interpret folders vs files via icons if we had them, or just text
                self.tree.insert("", "end", text=name, values=(size_str,))
                
        except Exception as e:
            print(f"Error listing directory: {e}")
