with open("check.log", "w") as f:
    try:
        import numpy
        f.write("numpy ok\n")
        import pandas
        f.write("pandas ok\n")
        import sklearn
        f.write("sklearn ok\n")
    except Exception as e:
        import traceback
        f.write(traceback.format_exc())
