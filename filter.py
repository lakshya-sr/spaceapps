import pandas as pd
#import matplotlib.pyplot as plt
import math



def avg(l):
    return sum(l)/len(l)

def rms(l):
    return math.sqrt(avg([x**2 for x in l]))


def calculate_quake_time(data,params):
    vel = data["velocity(m/s)"].abs().rolling(params["window_size"]).mean().diff()
    time = data["time_rel(sec)"]

    mean = vel.mean()
    std_dev = math.sqrt(((vel - mean)**2).mean()) # Standard Deviation
    detections = vel > std_dev*params["threshold"] # filtered values
    first_detection = time[detections.idxmax()] # Detected time

    return first_detection - params["offset"]
    
    # Other approaches which did not work

    # last_detection = time[detections[::-1].idxmax()]
    # offset = (last_detection - first_detection)/params["offset_multiplier"]

    # true_values = []
    # for i, d in enumerate(detections):
    #     if d:
    #         true_values.append(i)

 
    # curr_cluster = [true_values[0]]
    # clusters = [[true_values[0]]]

    # for i in true_values:
    #     if i - curr_cluster[-1] > params["cluster_threshold"]:
    #         clusters.append(curr_cluster)
    #         curr_cluster = []
        
    #     curr_cluster.append(i)

    # largest_cluster = max(clusters)
    # print(len(clusters))
    # return time[largest_cluster[0]]



def evaluate_files(catalog, data_folder, params):
    test_data = pd.read_csv(catalog)
    errors = {}
    detections = {}
    for file, time in zip(test_data["filename"],test_data["time_rel(sec)"]):
        try:
            data = pd.read_csv(f"{data_folder}/{file}.csv")
            detections[file] = calculate_quake_time(data,params)
            errors[file] = detections[file] - time
            print(errors[file])
        except FileNotFoundError:
            continue
        except KeyboardInterrupt:
            break
    return errors, detections

import blackbox as bb

# Optimization function
def fun(x):
    params = {"threshold":x[0], "window_size":round(x[1]), "offset":x[2]}
    data_folder = "dataset"
    catalog_file = "apollo12_catalog_GradeA_final.csv"
    errors = evaluate_files(catalog_file, data_folder, params)[0]
    
    return rms([v for v in errors.values() if v < 1000])

# Parameter optimization
if __name__ == "__main__":
    import pickle
    if input("Evaluate(e)/Optimize Parameters(o)? ") == "o":
        domain = [[1, 20], [1, 1000], [0, 500]]
        result = bb.minimize(f=fun, domain=domain, budget=32, batch=4)

        best = {"threshold":result["best_x"][0], "window_size":round(result["best_x"][1]), "offset":result["best_x"][2]} 
        print(best) # best parameters
        f = open("best-params", "wb")
        pickle.dump(best,f)
        f.close()
        print(result["best_f"])
    else:
        f = open("best-params", "rb")
        params = pickle.load(f)
        f.close()
        catalog_file = "apollo12_catalog_GradeA_final.csv"
        errors, detections = evaluate_files(catalog_file, "dataset", params)

        # Data writing

        import csv
        f = open("detections.csv", "w")
        w = csv.writer(f)
        w.writerow(["filename", "time_rel(sec)"])
        for file, time in detections.items():
            w.writerow([file, time])
        f.close()


        f = open("errors.csv","w")
        w = csv.writer(f)
        w.writerow(["filename","error"])
        for file, error in errors.items():
            w.writerow([file, error])
        f.close()
