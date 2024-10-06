import pandas as pd
import matplotlib.pyplot as plt
import math



def avg(l):
    return sum(l)/len(l)

def rms(l):
    return math.sqrt(avg([x**2 for x in l]))


def calculate_quake_time(data,params):
    vel = data["velocity(m/s)"].abs().rolling(params["window_size"]).mean().diff()
    time = data["time_rel(sec)"]

    mean = vel.mean()
    std_dev = math.sqrt(((vel - mean)**2).mean())
    detections = vel > std_dev*params["threshold"]
    first_detection = time[detections.idxmax()]

    #return first_detection
    last_detection = time[detections[::-1].idxmax()]
    offset = (last_detection - first_detection)/params["offset_multiplier"]

    true_values = []
    for i, d in enumerate(detections):
        if d:
            true_values.append(i)

 
    curr_cluster = [true_values[0]]
    clusters = [[true_values[0]]]

    for i in true_values:
        if i - curr_cluster[-1] > params["cluster_threshold"]:
            clusters.append(curr_cluster)
            curr_cluster = []
        
        curr_cluster.append(i)

    largest_cluster = max(clusters)
    print(len(clusters))
    return time[largest_cluster[0]]



params = {"threshold":10, "window_size":1, "offset_multiplier":10, "cluster_threshold":500}
data_folder = "data/lunar/training"
test_data = pd.read_csv(f"{data_folder}/catalogs/apollo12_catalog_GradeA_final.csv")
scores = {}
detections = {}
for file, time in zip(test_data["filename"],test_data["time_rel(sec)"]):
    try:
        data = pd.read_csv(f"{data_folder}/data/S12_GradeA/{file}.csv")
        detections[file] = calculate_quake_time(data,params)
        scores[file] = detections[file] - time
        print(scores[file])
    except FileNotFoundError:
        continue
    except KeyboardInterrupt:
        break

import csv
f = open("final.csv", "w")
w = csv.writer(f)
w.writerow(["filename", "time_rel(sec)"])
for file, time in detections.items():
    w.writerow([file, time])
f.close()


f = open("scores","w")
w = csv.writer(f)
w.writerow(["filename","score"])
for file, score in scores.items():
    w.writerow([file, score])
f.close()



"""
data = pd.read_csv("data/lunar/training/data/S12_GradeA/xa.s12.00.mhz.1970-01-19HR00_evid00002.csv")
plt.plot(calculate_quake_time(data,{"threshold":10}))
plt.show()

"""

import blackbox as bb


def fun(x):
    data_folder = "data/lunar/training"
    test_data = pd.read_csv(f"{data_folder}/catalogs/apollo12_catalog_GradeA_final.csv")
    scores = {}
    detections = {}
    for file, time in zip(test_data["filename"],test_data["time_rel(sec)"]):
        try:
            data = pd.read_csv(f"{data_folder}/data/S12_GradeA/{file}.csv")
            detections[file] = calculate_quake_time(data,params)
            scores[file] = detections[file] - time
            print(scores[file])
        except FileNotFoundError:
            continue
        except KeyboardInterrupt:
            break
    return rms(scores.values())


if __name__ == "__main__":
    domain = [[1, 20], [1, 1000]]
    result = bb.minimize(f=fun, domain=domain, budget=20, batch=4)

    print(result["best_x"])
    print(result["best_f"])
