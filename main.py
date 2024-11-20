import csv
from collections import defaultdict
# check intersections
# check approachability
# check volume
# check support


def parse_csv(filename):
    data = []
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # change values for rotated boxes and add relevant values to the array
            if int(row["rotation"]) == 1:
                data.append(
                    {
                        "id": int(row["No."]),
                        "sizeX": int(row["sizeY"]),
                        "sizeY": int(row["sizeX"]),
                        "sizeZ": int(row["sizeZ"]),
                        "posX": int(row["posX"]),
                        "posY": int(row["posY"]),
                        "posZ": int(row["posZ"]),
                    }
                )
            else:
                data.append(
                    {
                        "id": int(row["No."]),
                        "sizeX": int(row["sizeX"]),
                        "sizeY": int(row["sizeY"]),
                        "sizeZ": int(row["sizeZ"]),
                        "posX": int(row["posX"]),
                        "posY": int(row["posY"]),
                        "posZ": int(row["posZ"]),
                    }
                )
    return data


def check_volume(data):
    initialized = False
    min_x = 0
    max_x = 0
    min_y = 0
    max_y = 0
    min_z = 0
    max_z = 0
    volume = 0
    for box in data:
        # update the values assuming there are no intersections
        volume += box["sizeX"] * box["sizeY"] * box["sizeZ"]
        if initialized:
            min_x = min(min_x, box["posX"] - box["sizeX"] // 2)
            min_y = min(min_y, box["posY"] - box["sizeY"] // 2)
            min_z = min(min_z, box["posZ"] - box["sizeZ"] // 2)

            max_x = max(max_x, box["posX"] + box["sizeX"] // 2)
            max_y = max(max_y, box["posY"] + box["sizeY"] // 2)
            max_z = max(max_z, box["posZ"] + box["sizeZ"] // 2)
        else:
            initialized = True
            min_x = box["posX"] - box["sizeX"] // 2
            min_y = box["posY"] - box["sizeY"] // 2
            min_z = box["posZ"] - box["sizeZ"] // 2

            max_x = box["posX"] + box["sizeX"] // 2
            max_y = box["posY"] + box["sizeY"] // 2
            max_z = box["posZ"] + box["sizeZ"] // 2

    total_volume = (max_x - min_x) * (max_y - min_y) * (max_z - min_z)
    percentage_volume = volume / total_volume
    return volume, total_volume, percentage_volume


data = parse_csv("in0.csv")
volume, total_volume, percentage_volume = check_volume(data)

if percentage_volume > 0.5:
    print(
        "volume criterion PASSED: sum of volumes =",
        volume,
        ", total volume =",
        total_volume,
        ", percentage =",
        percentage_volume,
    )
else:
    print(
        "volume criterion FAILED: sum of volumes =",
        volume,
        ", total volume =",
        total_volume,
        ", percentage =",
        percentage_volume,
    )
