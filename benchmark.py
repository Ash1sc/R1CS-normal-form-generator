import os
import shutil

from_path = "./benchmark"
to_path = "./new_benchmark"

files = os.listdir(from_path)

if not os.path.exists(to_path):
    os.makedirs(to_path)

for f in files:

    if f.endswith(".py"):
        continue

    path = from_path + "/" + f

    if not os.path.exists(to_path + "/" + f):
        os.makedirs(to_path + "/" + f)

    txts = os.listdir(path)
    num = 1
    for i in range(len(txts)):
        for j in range(i + 1, len(txts)):
            txt1 = path + "/" + txts[i]
            txt2 = path + "/" + txts[j]

            if not os.path.exists(to_path + "/" + f + "/" + str(num)):
                os.makedirs(to_path + "/" + f + "/" + str(num))

            # 复制文件
            shutil.copy(txt1, to_path + "/" + f + "/" + str(num) + "/" + str(1) + ".txt")
            shutil.copy(txt2, to_path + "/" + f + "/" + str(num) + "/" + str(2) + ".txt")
            num += 1
