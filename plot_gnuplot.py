from pathlib import Path
import os
import subprocess

script_file = os.listdir(Path("gnuplot_script"))
full_path_to_script = Path("gnuplot_script", "{}".format(script_file[0])).absolute()
result = subprocess.run(["gnuplot", "-c", "{}".format(full_path_to_script), "-platform wayland"])

