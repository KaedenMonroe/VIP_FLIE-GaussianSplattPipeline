from enum import Enum
from typing import List
from sections.base_section import PipelineSection

class SelectionMode(Enum):
    """
    Used to define the selection type for a category
    """
    SINGLE = "single"  # Radio button behavior
    MULTI = "multi"    # Checkbox behavior

class PipelineCategory:
    """
    Groups multiple PipelineSections together.
    e.g., 'Preprocessing' category containing 'BlurFilter' and 'FrameExtract'.
    !!!This is the initial object declaration, not where you define categories!!!
    To create a Category, declare it in main
    """
    def __init__(self, name: str, selection_mode: SelectionMode, stage_index: int):
        self.name = name
        self.selection_mode = selection_mode
        self.stage_index = stage_index  # 1=Prep, 2=SfM, etc. (For ordering checks)
        self.sections: List[PipelineSection] = []

    def add_section(self, section: PipelineSection):
        self.sections.append(section)
