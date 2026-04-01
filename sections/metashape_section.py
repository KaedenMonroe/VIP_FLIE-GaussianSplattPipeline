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
        self._add_entry(parent, "Metashape File Name:", "name")
        self._add_checkbox(parent, "Save Metashape file in a seperate Directory?", "separateDirFlag", default_val=False)
        self._add_folder_selector(parent, "Select Seperate Metashape File Directory (optional):", "metashape_output")
        #TODO: Add more options and incorporate them into the metashape execution file
        

    def build_command(self) -> List[str]:
             
        from core.command_builders import MetashapeCommandBuilder
        return MetashapeCommandBuilder.build(self.config.get_section_config(self.name))
    
    def validate(self) -> bool:
        #TODO: create validation
        cfg = self.config.get_section_config(self.name)
        try:
            d = float(cfg.get("duration", 0))
            if d < 0:
                print("Duration must be positive")
                return False
        except ValueError:
            return False
            
        return True
