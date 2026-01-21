from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import os

@dataclass
class GlobalContext:
    """
    Holds high-level paths and global settings accessible by all sections.
    """
    project_root: str = ""
    input_video_path: str = ""
    input_dir: str = ""
    output_dir: str = ""
    
    # You can add more global flags here

    def validate(self) -> bool:
        """Simple validation to check if critical paths are set."""
        if not self.input_video_path:
            return False
        return True

@dataclass
class PipelineConfiguration:
    """
    The main Model for the application.
    Stores the configuration for every section.
    """
    global_context: GlobalContext = field(default_factory=GlobalContext)
    
    # Key = Section Name (e.g., "Preprocessing"), Value = Dict of settings
    section_settings: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def get_section_config(self, section_name: str) -> Dict[str, Any]:
        if section_name not in self.section_settings:
            self.section_settings[section_name] = {}
        return self.section_settings[section_name]

    def update_section_config(self, section_name: str, key: str, value: Any):
        config = self.get_section_config(section_name)
        config[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for saving to JSON/YAML."""
        return {
            "global": self.global_context.__dict__,
            "sections": self.section_settings
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineConfiguration':
        """Load from a dictionary."""
        config = cls()
        if "global" in data:
            config.global_context = GlobalContext(**data["global"]) # dictionary unpacking
        if "sections" in data:
            config.section_settings = data["sections"]
        return config
