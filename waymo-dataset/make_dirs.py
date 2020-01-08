import os

for i in range(25,26):
    dir_path ="C:/Users/lab-detection/Desktop/dataset/figure" + str(i)
    print(dir_path)
    os.mkdir(dir_path)
