from typing import List
import tkinter as tk
import sys
from .base_section import PipelineSection

class MetashapeSection(PipelineSection):
    """
    Passes the dataset to metashape for colmap data
    """
    def __init__(self, name: str, config):
        super().__init__(name, config)
        
    def render_options(self, parent: tk.Frame):
        # Passes options for 
        self._add_entry(parent, "File Name:", "name")
        self._add_entry(parent, "Metashape File Directory", "metashape_dir")
        #TODO: Add more options and incorporate them into the metashape execution file
        

    def build_command(self) -> List[str]:
        #TODO: make sure neccesary script inputs are avalible: 
        #   Added: name, metashape_directory
        #   Needed: export_path, import path(photos)
        cfg = self.config.get_section_config(self.name)
        filename = cfg.get("name", "metashapefile")
        metashape_dir = cfg.get("message", "Hello")
     
        return [sys.executable, "-c", code]
    
    def validate(self) -> bool:
        # Example validation
        cfg = self.config.get_section_config(self.name)
        try:
            d = float(cfg.get("duration", 0))
            if d < 0:
                print("Duration must be positive")
                return False
        except ValueError:
            return False
            
        return True
