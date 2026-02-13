import tkinter as tk
import queue
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from core.state_models import PipelineConfiguration
from core.executor import AsyncExecutor
from core.pipeline_manager import PipelineManager
from core.category import PipelineCategory, SelectionMode
from gui.app_window import AppWindow

# Sections
# Sections
from sections.example_section import ExampleSection
from sections.blur_section import BlurSection
from sections.extract_frames_section import ExtractFramesSection
from sections.deduplicate_section import DeduplicateSection

def main():
    output_queue = queue.Queue()
    config = PipelineConfiguration()
    executor = AsyncExecutor(output_queue)
    manager = PipelineManager(config, executor)
    
    # --- Define Categories & Sections ---
    
    # 1. Preprocessing (Multi-Select allowed)
    cat_prep = PipelineCategory("Preprocessing", SelectionMode.MULTI, stage_index=1)
    cat_prep.add_section(ExtractFramesSection("Frame Extraction", config))
    cat_prep.add_section(BlurSection("Blur Filter", config))
    cat_prep.add_section(DeduplicateSection("Deduplicate Frames", config))
    manager.add_category(cat_prep)
    
    # 2. SfM (Single Select implied)
    cat_sfm = PipelineCategory("Structure from Motion", SelectionMode.SINGLE, stage_index=2)
    cat_sfm.add_section(ExampleSection("COLMAP", config))
    cat_sfm.add_section(ExampleSection("GLOMAP (Global)", config))
    manager.add_category(cat_sfm)
    
    # 3. Training
    cat_train = PipelineCategory("Training", SelectionMode.SINGLE, stage_index=3)
    cat_train.add_section(ExampleSection("Standard 3DGS", config))
    manager.add_category(cat_train)
    
    # --- Launch ---
    app = AppWindow(manager, executor, output_queue)
    
    def on_close():
        executor.stop()
        app.destroy()
        
    app.protocol("WM_DELETE_WINDOW", on_close)
    app.mainloop()

if __name__ == "__main__":
    main()
