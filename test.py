import sys
sys.path.append(r"D:\Hackathon\Project 3\backend")
from startup_train import train_model

try:
    train_model()
    print("SUCCESS!!")
except Exception as e:
    import traceback
    traceback.print_exc()
