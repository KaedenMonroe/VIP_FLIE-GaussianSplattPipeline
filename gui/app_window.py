import tkinter as tk
import queue

from core.pipeline_manager import PipelineManager
from core.executor import AsyncExecutor
from .console_widget import ConsoleWidget
from .section_frames import SectionFrame
from .library_widget import LibraryWidget
from .preview_widget import PreviewWidget
from .path_selection_window import PathSelectionWindow

class AppWindow(tk.Tk):
    """
    GUI V2: 3-Panel Layout.
    [Library (Tree) | Settings (Forms) | Preview (List)]
    [               Console                            ]
    """
    def __init__(self, manager: PipelineManager, executor: AsyncExecutor, output_queue: queue.Queue):
        super().__init__()
        self.title("Gaussian Splatting Pipeline V2")
        self.geometry("1400x800")
        
        self.manager = manager
        self.executor = executor
        self.output_queue = output_queue
        self.window_manager_open = False
        self.win = None
        
        # Event wiring
        self.manager.add_staging_listener(self._on_global_staging_change)
        
        self._setup_ui()

    def _on_global_staging_change(self):
        # Update Preview Widget
        self.preview_widget.refresh()
        # Update Library Toggles (handled by its own listener, but safe to keep decoupling if needed)

    def _setup_ui(self):
        # Toolbar
        toolbar = tk.Frame(self, bd=1, relief=tk.RAISED)
        toolbar.pack(side='top', fill='x', padx=5, pady=5)
        
        # NOTE: Removed 'bg' kwarg which causes empty buttons on Mac
        tk.Button(toolbar, text="Run Staged Pipeline", command=lambda: self.manager.run_sequence()).pack(side='left', padx=5)
        tk.Button(toolbar, text="STOP", command=lambda: self.manager.stop_sequence()).pack(side='left', padx=5)
        
        # Separator / Spacer
        tk.Frame(toolbar, width=20).pack(side='left')
        
        tk.Button(toolbar, text="Set Input/Output Paths", command=self._open_path_selection).pack(side='left', padx=5)

        # Main Paned Window (Horizontal split: Left, Middle, Right)
        main_pane = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill='both', expand=True, padx=5, pady=5)

        # 1. Left: Library
        self.library_widget = LibraryWidget(main_pane, self.manager, on_view_section=self._show_section_options)
        self.library_widget.pack(fill='both', expand=True)
        main_pane.add(self.library_widget, minsize=250)

        # 2. Middle: Options
        self.options_container = tk.Frame(main_pane, bg='white', bd=1, relief=tk.SUNKEN)
        main_pane.add(self.options_container, minsize=400)

        # 3. Right: Preview
        self.preview_widget = PreviewWidget(main_pane, self.manager)
        main_pane.add(self.preview_widget, minsize=250)

        # Bottom: Console
        bottom_frame = tk.Frame(self, height=150)
        bottom_frame.pack(side='bottom', fill='x')
        self.console = ConsoleWidget(bottom_frame, self.output_queue)
        self.console.pack(fill='both', expand=True)

    def _show_section_options(self, section):
        # Clear container
        for widget in self.options_container.winfo_children():
            widget.destroy()
        
        # Render
        frame = SectionFrame(self.options_container, section)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        section.on_show()

        frame.pack(fill='both', expand=True, padx=20, pady=20)
        section.on_show()

    def _open_path_selection(self):
        if self.window_manager_open:
            self.win.lift()
        else:
            self.window_manager_open = True
            self.win = PathSelectionWindow(self, self.manager.config)
            self.win.set_callback(self.preview_widget.refresh)
            self.win.protocol("WM_DELETE_WINDOW", self._on_path_selection_closing)
        # Optional: Make it modal
        # win.transient(self)
        # win.grab_set()
    
    def _on_path_selection_closing(self):
        self.window_manager_open = False
        self.win.destroy()
        self.win = None
