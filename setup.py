import os
import shutil
from distutils.dir_util import copy_tree

from setuptools import find_packages, setup

# global variables
board = os.environ['BOARD']
board_notebooks_dir = '~/'
board_project_dir = os.path.join(board_notebooks_dir, 'smart_lock')

# check whether board is supported
def check_env():
    if not board == 'Ultra96':
        raise ValueError("Board {} is not supported.".format(board))
        
# check if the path already exists, delete if so
def check_path():
    if os.path.exists(board_project_dir):
        shutil.rmtree(board_project_dir)
    
check_env()
# check_path()

setup(
    name="smart_lock",
    version='1.0',
    install_requires=[
        'pynq>=2.5',
        'paho-mqtt>=1.5.0',
        'face-recognition>=1.3.0',
        'dlib>=19.21.0',
        'matplotlib>=3.3.0',
        # 'opencv-python>=4.3.0.38', pynq>=2.5 means you have opencv
    ],
    url='https://github.com/XilinxCannonFodderTeam/smart_lock',
    author="XilinxCannonFodderTeam",
    packages=find_packages(),
    description="This is a Smart_Lock Project using Ultra96_V2 and PYNQ.")