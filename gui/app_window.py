"""
Controls the Main GUI for the Application 
"""

import tkinter as tk
import queue
import os
from PIL import Image, ImageTk
from .style import Stylemanager, bgColor
from core.pipeline_manager import PipelineManager
from core.executor import AsyncExecutor
from .console_widget import ConsoleWidget
from .section_frames import SectionFrame
from .library_widget import LibraryWidget
from .preview_widget import PreviewWidget
from .path_selection_window import PathSelectionWindow


class AppWindow(tk.Tk):
    """
    Main Object for the app layout
    
    GUI V2: 3-Panel Layout.
    [Library (Tree) | Settings (Forms) | Preview (List)]
    [               Console                            ]
    """
    def __init__(self, manager: PipelineManager, executor: AsyncExecutor, output_queue: queue.Queue):
        super().__init__()
        self.title("Gaussian Splatting Pipeline V2")
        self.geometry("1400x800")
        current_dir = os.getcwd()
        img1 = tk.PhotoImage(file=current_dir+"\\gui\\images\\icon128x128.png")
        img2 = tk.PhotoImage(file=current_dir+"\\gui\\images\\icon256x256.png")
        self.iconphoto(True, img1, img2)
        self.manager = manager
        self.executor = executor
        self.output_queue = output_queue
        self.window_manager_open = False
        self.win = None
        self.stylemanager = Stylemanager()
        self.stylemanager.styleMain(self)
        self.configure(background=bgColor)
        # Event wiring
        self.manager.add_staging_listener(self._on_global_staging_change)
        
        
        self._setup_ui()

    def _on_global_staging_change(self):
        # Update Preview Widget
        self.preview_widget.refresh()
        # Update Library Toggles (handled by its own listener, but safe to keep decoupling if needed)

    def _setup_ui(self):
        """
        Sets up the main GUI after the main window is created
        """
        # Toolbar
        toolbar = tk.Frame(self, bd=0)
        toolbar.pack(side='top', fill='x', padx=0, pady=0)
        self.stylemanager.styleToolbar(toolbar)
        
        
        # NOTE: Removed 'bg' kwarg which causes empty buttons on Mac
        runButton = tk.Button(toolbar, text="Run-Pipeline", command=lambda: self.manager.run_sequence(), bd=0)
        runButton.pack(side='left', padx=(10,0), pady=5, ipadx=1, ipady=1)
        estopButton = tk.Button(toolbar, text="E-Stop", command=lambda: self.manager.stop_sequence(), bd=0)
        estopButton.pack(side='left', padx=(10,0), pady=5, ipadx=1, ipady=1)
        self.stylemanager.styleButton(estopButton)
        self.stylemanager.styleButton(runButton)
        
        pathsbutton = tk.Button(toolbar, text="Set-Paths", command=self._open_path_selection, bd=0)
        pathsbutton.pack(side='left', padx=(10,0), pady=5, ipadx=1, ipady=1)
        self.stylemanager.styleButton(pathsbutton)
        

        # Main Paned Window (Horizontal split: Left, Middle, Right)
        main_pane = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill='both', expand=True, padx=5, pady=5)
        main_pane.configure(background=bgColor, relief="flat", sashrelief='raised')

        # 1. Left: Library
        self.library_widget = LibraryWidget(main_pane, self.manager, on_view_section=self._show_section_options)
        main_pane.add(self.library_widget, minsize=240, width=250)
        self.library_widget.configure(borderwidth=0)
        
        
        # 2. Middle: Options
        self.options_container = tk.Frame(main_pane, bg=bgColor)
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
        """
        Renders the config for each section when its clicked on
        """ 
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
        """
        Opens the window to select input output folders
        Also checks to see if the window is already open and if so,
        brings it to the front
        """
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
        """
        Destroys the path selection window object on close and 
        sets the flag back to false so a new window can open
        """
        self.window_manager_open = False
        self.win.destroy()
        self.win = None
        
