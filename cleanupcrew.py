import os
import random
import shutil

def createInitialDirs(required_dirs):
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)

def generateRandomSuffix():
    num = random.random()
    return str(num).replace("0.", "", 1)

def janitor(dir):
    if os.path.exists(dir):
        for filename in os.listdir(dir):
            file_path = os.path.join(dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Error cleaning up {file_path}. {e}")
        print(f"Cleaned up {dir} successfully :D")
    else:
        print(f"Directory {dir} doesn't exist. Nothing to clean.")