# %%
import matplotlib.pyplot as plt
import pandas as pd

detections = pd.read_csv("detections.csv")

files = [pd.read_csv(f"dataset/{file}.csv") for file in detections["filename"]]
for data, detection, filename in zip(files,detections["time_rel(sec)"], detections["filename"]):
    plt.plot(data["time_rel(sec)"], data["velocity(m/s)"])
    plt.axvline(x=detection, color="red")
    plt.savefig(filename+".png")
    plt.clf()
# plt.show()
# print(detections[0]["time_rel(sec)"])
# %%
