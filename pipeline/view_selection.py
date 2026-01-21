import subprocess
from config import get_env_executable

class TrajSelection:
    '''
    routes out to Indoor Traj Frame Selection so GUI can interact
    '''
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        pass
    def run(self):
        # We might want to use a specific python environment for this too
        python_exe = get_env_executable("IndoorTraj")
        script_path = "scripts/IndoorTraj/main.py" # Adjusted path

        command = [python_exe, script_path, "--input-dir", self.input_dir, "--out-dir", self.output_dir]

        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error running Indoor Traj Frame Selection: {e}")

    pass