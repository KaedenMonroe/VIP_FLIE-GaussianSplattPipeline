import sys
import os
from typing import List, Dict, Any

class BlurCommandBuilder:
    @staticmethod
    def build(config: Dict[str, Any]) -> List[str]:
        """
        Builds the command line arguments for the Blur Filter script.
        """
        # Resolve script path relative to this file
        # This file is in core/
        # Scripts are in scripts/
        # Path: ../scripts/blur_filter.py
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # base_dir is now the project root
        script_path = os.path.join(base_dir, "scripts", "blur_filter.py")
        
        cmd = [sys.executable, script_path]
        
        # injected paths
        if "input_dir" in config:
            cmd.extend(["--input_dir", str(config["input_dir"])])
        
        if "output_dir" in config:
            cmd.extend(["--output_dir", str(config["output_dir"])])
            
        # Optional args
        
        # Target Count
        if "target_count" in config:
            try:
                tc = float(config["target_count"])
                if tc > 0:
                    cmd.extend(["--target_count", str(int(tc))])
            except (ValueError, TypeError):
                pass
                
        # Keep Percentage
        if "target_percentage" in config:
            try:
                tp = float(config["target_percentage"])
                # Heuristic: If value > 1.0, assume it is 0-100 range and normalize
                if tp > 1.0:
                    tp = tp / 100.0
                cmd.extend(["--keep_percent", str(tp)])
            except (ValueError, TypeError):
                pass

        # Groups
        if "groups" in config:
            try:
                g = float(config["groups"])
                if g > 0:
                    cmd.extend(["--groups", str(int(g))])
            except (ValueError, TypeError):
                pass
                
        # Dry Run
        # Checkbox usually stores boolean or 0/1
        dr = config.get("dry_run", False)
        # It might be a string "0" or "1" or "False" if coming from some UI save
        if str(dr).lower() in ("true", "1", "yes"):
             cmd.append("--dry_run")

        return cmd

class DeduplicateCommandBuilder:
    @staticmethod
    def build(config: Dict[str, Any]) -> List[str]:
        """
        Builds the command line arguments for the Deduplicate script.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # base_dir is project root
        script_path = os.path.join(base_dir, "scripts", "deduplicate.py")
        
        cmd = [sys.executable, script_path]
        
        # Injected paths
        # Deduplicate script mainly needs input_dir. 
        # For chaining, if this follows Blur, 'input_dir' here is the 'output_dir' of Blur.
        if "input_dir" in config:
            cmd.extend(["--input_dir", str(config["input_dir"])])

        if "output_dir" in config:
            cmd.extend(["--output_dir", str(config["output_dir"])])
            
        # Threshold
        if "threshold" in config:
            try:
                th = float(config["threshold"])
                # Boundary checks if needed
                if 0.0 <= th <= 1.0:
                    cmd.extend(["--threshold", str(th)])
            except (ValueError, TypeError):
                pass

        # Resolution (resize_width)
        if "resolution" in config:
            try:
                # The GUI Dropdown likely returns an int or string "512"
                res = int(config["resolution"])
                if res > 0:
                    cmd.extend(["--resize_width", str(res)])
            except (ValueError, TypeError):
                pass
                
        # Dry Run
        dr = config.get("dry_run", False)
        if str(dr).lower() in ("true", "1", "yes"):
             cmd.append("--dry_run")
             
        # Max Workers (default to 2 for Windows compatibility)
        if "max_workers" in config:
            try:
                mw = int(config["max_workers"])
                if mw > 0:
                    cmd.extend(["--max_workers", str(mw)])
            except (ValueError, TypeError):
                pass
        else:
            # Default to 2 workers to avoid paging file issues on Windows
            cmd.extend(["--max_workers", "2"])

        return cmd

class ExtractFramesCommandBuilder:
    @staticmethod
    def build(config: Dict[str, Any]) -> List[str]:
        """
        Builds the command line arguments for the Extract Frames script.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # base_dir is project root
        script_path = os.path.join(base_dir, "scripts", "extract_frames.py")
        
        cmd = [sys.executable, script_path]
        
        # Mandatory Arguments
        if "input_dir" in config:
            cmd.extend(["--input_dir", str(config["input_dir"])])
            
        if "output_dir" in config:
            cmd.extend(["--output_dir", str(config["output_dir"])])
            
        # Optional Arguments
        if "format" in config:
            # Dropdown value e.g. "jpg"
            cmd.extend(["--format", str(config["format"])])
            
        if "every_n" in config:
            try:
                n = int(config["every_n"])
                if n > 1:
                    cmd.extend(["--every_n", str(n)])
            except (ValueError, TypeError):
                pass
            
        # Dry Run
        dr = config.get("dry_run", False)
        if str(dr).lower() in ("true", "1", "yes"):
             cmd.append("--dry_run")

        return cmd
