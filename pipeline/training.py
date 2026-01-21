from abc import ABC, abstractmethod
import subprocess
import os
from config import get_env_executable

# TODO: Set this to the actual path of the training script
train_py_path = os.path.abspath("scripts/FastGS/train.py")

class Training(ABC):
    def __init__(self, sparse_dir, model_dir):
        self.sparse_dir = sparse_dir
        self.model_dir = model_dir
        self.quality = "standard" # Default quality
        pass

    @abstractmethod # child classes must implement this function
    def train(self):
        pass

    def run(self):
        self.train()
        pass

class FastGS(Training):
    '''
    trains the model using FastGS

    requests Standard vs High Quality from GUI
    '''
    def train(self):
        '''
        runs FastGS through command line
        Args:
            train_py_path
            sparse_dir
            model_output_dir
            quality
        '''
        python_exe = get_env_executable("FastGS")

        # Base command
        cmd = [
            python_exe, train_py_path,
            "-s", self.sparse_dir,
            "-m", self.model_dir,
            "--quiet"
        ]

        # Quality Adjustments
        if self.quality == "high":
            # -r 1: Use original image resolution (no downscaling)
            # --loss_thresh: Slightly lower threshold to keep more detail
            cmd += [
                "-r", "1", 
                "--loss_thresh", "0.0001" 
            ]
        else:
            # -r 4: Downscale images by 4x for speed
            # --loss_thresh: Standard threshold
            cmd += [
                "-r", "4",
                "--loss_thresh", "0.0005"
            ]
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")



    