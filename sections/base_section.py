from abc import ABC, abstractmethod
import tkinter as tk
from typing import List, Any, Dict, Optional
from core.state_models import PipelineConfiguration

class PipelineSection(ABC):
    """
    Abstract Base Class for a single step in the pipeline.
    Enforces the interface for Rendering Options and Building Commands.
    """
    def __init__(self, name: str, config: PipelineConfiguration):
        self.name = name
        self.config = config
        
        # Internal storage for widgets so we can read them later
        # Key = Config Key, Value = Tkinter Variable (StringVar, IntVar, etc.)
        self.widget_vars: Dict[str, tk.Variable] = {}
        
        # Chaining paths
        self.input_path: str = ""
        self.output_path: str = ""

    @abstractmethod
    def render_options(self, parent: tk.Frame):
        """
        Draw the configuration widgets for this section into `parent`.
        Should verify if config keys exist, if not, set defaults.
        """
        pass

    def set_paths(self, input_path: str, output_path: str):
        """Called by PipelineManager to inject chained paths."""
        self.input_path = input_path
        self.output_path = output_path
        
        # We also update the config so the GUI (if open) reflects this, 
        # or at least so the build_command can find it.
        self.config.update_section_config(self.name, "input_dir", input_path)
        self.config.update_section_config(self.name, "output_dir", output_path)

    @abstractmethod
    def build_command(self) -> List[str]:
        """
        Constructs the strict command line arguments string list.
        e.g., ['python', 'script.py', '--input', '...']
        Requires reading from self.config (or self.widget_vars if they are synced).
        """
        pass

    def validate(self) -> bool:
        """
        Override this to check if necessary inputs exist (files, paths)
        before running.
        """
        return True

    def on_show(self):
        """Called when this section is selected in the UI sidebar."""
        pass

    # --- Helper methods for Widgets ---
    
    def _add_entry(self, parent: tk.Frame, label_text: str, config_key: str, default_val: str = ""):
        """Helper to create a Label + Entry row."""
        frame = tk.Frame(parent)
        frame.pack(fill='x', pady=2)
        
        lbl = tk.Label(frame, text=label_text, width=20, anchor='e')
        lbl.pack(side='left', padx=5)
        
        # Load current value from config or default
        current_val = self.config.get_section_config(self.name).get(config_key, default_val)
        
        var = tk.StringVar(value=str(current_val))
        self.widget_vars[config_key] = var
        
        # Trace changes to update config immediately
        var.trace_add("write", lambda *args: self.config.update_section_config(self.name, config_key, var.get()))
        
        entry = tk.Entry(frame, textvariable=var)
        entry.pack(side='left', fill='x', expand=True, padx=5)

    def _add_checkbox(self, parent: tk.Frame, label_text: str, config_key: str, default_val: bool = False):
        """Helper to create a Checkbox."""
        frame = tk.Frame(parent)
        frame.pack(fill='x', pady=2)
        
        current_val = self.config.get_section_config(self.name).get(config_key, default_val)
        var = tk.BooleanVar(value=current_val)
        self.widget_vars[config_key] = var
        
        var.trace_add("write", lambda *args: self.config.update_section_config(self.name, config_key, var.get()))
        
        chk = tk.Checkbutton(frame, text=label_text, variable=var)
        chk.pack(side='left', padx=25) # Offset to align somewhat with entries

    def _add_dropdown(self, parent: tk.Frame, label_text: str, config_key: str, options: List[str], default_val: str, width: int = None):
        """Helper to create a Dropdown (OptionMenu)."""
        frame = tk.Frame(parent)
        frame.pack(fill='x', pady=2)
        
        lbl = tk.Label(frame, text=label_text, width=20, anchor='e')
        lbl.pack(side='left', padx=5)
        
        current_val = self.config.get_section_config(self.name).get(config_key, default_val)
        if current_val not in options and options:
             current_val = options[0]

        var = tk.StringVar(value=current_val)
        self.widget_vars[config_key] = var
        
        var.trace_add("write", lambda *args: self.config.update_section_config(self.name, config_key, var.get()))
        
        menu = tk.OptionMenu(frame, var, *options)
        
        if width:
            menu.config(width=width)
            menu.pack(side='left', padx=5)
        else:
            menu.pack(side='left', fill='x', expand=True, padx=5)

    def _add_float_spinbox(self, parent: tk.Frame, label_text: str, config_key: str, 
                           min_val: float, max_val: float, step: float, default_val: float):
        """Helper to create a Float Spinbox (up/down arrows)."""
        frame = tk.Frame(parent)
        frame.pack(fill='x', pady=2)
        
        lbl = tk.Label(frame, text=label_text, width=20, anchor='e')
        lbl.pack(side='left', padx=5)
        
        current_val = self.config.get_section_config(self.name).get(config_key, default_val)
        
        # Ensure value is float for consistency
        try:
            current_val = float(current_val)
        except (ValueError, TypeError):
            current_val = float(default_val)

        var = tk.DoubleVar(value=current_val)
        self.widget_vars[config_key] = var
        
        var.trace_add("write", lambda *args: self.config.update_section_config(self.name, config_key, var.get()))
        
        # width=10 is approx half of a typical entry that expands
        sb = tk.Spinbox(frame, from_=min_val, to=max_val, increment=step,
                        textvariable=var, format="%.2f", width=10)
        sb.pack(side='left', padx=5)  # No expand=True, so it stays small

    def _add_int_spinbox(self, parent: tk.Frame, label_text: str, config_key: str, 
                         min_val: int, max_val: int, step: int, default_val: int):
        """Helper to create an Integer Spinbox."""
        frame = tk.Frame(parent)
        frame.pack(fill='x', pady=2)
        
        lbl = tk.Label(frame, text=label_text, width=20, anchor='e')
        lbl.pack(side='left', padx=5)
        
        current_val = self.config.get_section_config(self.name).get(config_key, default_val)
        try:
            current_val = int(float(current_val))
        except (ValueError, TypeError):
            current_val = int(default_val)

        var = tk.IntVar(value=current_val)
        self.widget_vars[config_key] = var
        
        var.trace_add("write", lambda *args: self.config.update_section_config(self.name, config_key, var.get()))
        
        sb = tk.Spinbox(frame, from_=min_val, to=max_val, increment=step,
                        textvariable=var, width=10)
        sb.pack(side='left', padx=5)
