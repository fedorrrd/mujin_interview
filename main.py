import csv
import sys
from collections import defaultdict


class Evaluator:
    def __init__(self, filename):
        # read the file
        self.data = self._parse_csv(filename)
        # find the bounding box surrounding all boxes (used for criterion 3)
        # and the smallest dimensions of all the boxes (used for criterion 1 in the grid system)
        # and the sum of the volumes of all the boxes (used for criterion 3)
        self.total_bounding_box, self.min_dimensions, self.sum_volumes = (
            self._preprocessor()
        )
        # initialize the grid (for criterions 1 and 4)
        self.grid = None

    def _parse_csv(self, filename):
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

    def _preprocessor(self):
        initialized = False
        # values for the total bounding box
        total_min_x = 0
        total_max_x = 0
        total_min_y = 0
        total_max_y = 0
        total_min_z = 0
        total_max_z = 0
        # values for smallest dimensions
        min_size_x = 0
        min_size_y = 0
        min_size_z = 0
        # values for sum of volume
        sum_volumes = 0

        for box in self.data:
            volume = box["sizeX"] * box["sizeY"] * box["sizeZ"]
            sum_volumes += volume
            # update the values assuming there are no intersections
            if initialized:
                min_x, min_y, min_z, max_x, max_y, max_z = self.bounding_box(box)
                total_min_x = min(total_min_x, min_x)
                total_min_y = min(total_min_y, min_y)
                total_min_z = min(total_min_z, min_z)
                total_max_x = max(total_max_x, max_x)
                total_max_y = max(total_max_y, max_y)
                total_max_z = max(total_max_z, max_z)

                min_size_x = min(min_size_x, box["sizeX"])
                min_size_y = min(min_size_y, box["sizeY"])
                min_size_z = min(min_size_z, box["sizeZ"])
            else:
                initialized = True
                (
                    total_min_x,
                    total_min_y,
                    total_min_z,
                    total_max_x,
                    total_max_y,
                    total_max_z,
                ) = self.bounding_box(box)

                min_size_x = box["sizeX"]
                min_size_y = box["sizeY"]
                min_size_z = box["sizeZ"]

        # update the total bounding box
        total_bounding_box = [
            total_min_x,
            total_min_y,
            total_min_z,
            total_max_x,
            total_max_y,
            total_max_z,
        ]

        return total_bounding_box, (min_size_x, min_size_y, min_size_z), sum_volumes

    def bounding_box(self, box):
        min_x = box["posX"] - box["sizeX"] // 2
        min_y = box["posY"] - box["sizeY"] // 2
        min_z = box["posZ"] - box["sizeZ"] // 2

        max_x = box["posX"] + box["sizeX"] // 2
        max_y = box["posY"] + box["sizeY"] // 2
        max_z = box["posZ"] + box["sizeZ"] // 2

        return (min_x, min_y, min_z, max_x, max_y, max_z)

    def create_grid(self):
        # initialize the grid
        self.grid = defaultdict(list)
        # use the dimensions of the smallest box as units
        (step_x, step_y, step_z) = self.min_dimensions

        for box in self.data:
            min_x, min_y, min_z, max_x, max_y, max_z = self.bounding_box(box)

            for x in range(min_x // step_x, max_x // step_x + 1):
                for y in range(min_y // step_y, max_y // step_y + 1):
                    for z in range(min_z // step_z, max_z // step_z + 1):
                        self.grid[(x, y, z)].append(box)

        return self.grid

    def check_intersection(self, box1, box2):
        min_x1, min_y1, min_z1, max_x1, max_y1, max_z1 = self.bounding_box(box1)
        min_x2, min_y2, min_z2, max_x2, max_y2, max_z2 = self.bounding_box(box2)

        # 2 boxes intersect if none the following os true
        return not (
            max_x1 <= min_x2  # box1 is to the left of box2
            or max_x2 <= min_x1  # box2 is to the left of box1
            or max_y1 <= min_y2  # box1 is closer than box2
            or max_y2 <= min_y1  # box2 is closer than box1
            or max_z1 <= min_z2  # box1 is lower than box2
            or max_z2 <= min_z1  # box2 is lower than box1
        )

    def check_obstructed(self, box1, box2):
        # check if box2 obtructs the access to box1
        min_x1, min_y1, min_z1, max_x1, max_y1, max_z1 = self.bounding_box(box1)
        min_x2, min_y2, min_z2, max_x2, max_y2, max_z2 = self.bounding_box(box2)

        # box2 obstructs box1 if box2 is higher than box1 and its projection on xy plane intersects box1
        return min_z2 > max_z1 and not (
            max_x1 <= min_x2
            or max_x2 <= min_x1
            or max_y1 <= min_y2
            or max_y2 <= min_y1  # refer to check_intersection
        )

    def check_supported(self, box1, box2):
        # check if box2 supports box1, return that and the part of the area, that is supported
        min_x1, min_y1, min_z1, max_x1, max_y1, max_z1 = self.bounding_box(box1)
        min_x2, min_y2, min_z2, max_x2, max_y2, max_z2 = self.bounding_box(box2)

        # the box is on the floor
        if min_z1 <= 5:
            return True, 1
        # box2 is lower then box1 and within 14 mm
        elif (min_z1 - max_z2) < 14 and (min_z1 - max_z2) > 0:
            # box1's projection overlaps with box2
            if (
                min_x1 < max_x2
                and max_x1 > min_x2
                and min_y1 < max_y2
                and max_y1 > min_y2
            ):
                covered_area = (min(max_x1, max_x2) - max(min_x1, min_x2)) * (
                    min(max_y1, max_y2) - max(min_y1, min_y2)
                )
                box1_area = box1["sizeX"] * box1["sizeY"]
                return True, covered_area / box1_area
            else:
                return False, 0

        else:
            return False, 0

    def criterion_intersection(self):
        if self.grid is None:
            self.grid = self.create_grid()
        # go through every cell in the grid and check any boxes assigned to the cell intersect
        for cell, cell_boxes in self.grid.items():
            for i in range(len(cell_boxes)):
                for j in range(i + 1, len(cell_boxes)):
                    if self.check_intersection(cell_boxes[i], cell_boxes[j]):
                        return True, cell_boxes[i], cell_boxes[j]
        # no boxes intersect
        return False, None, None

    def criterion_accessability(self):
        for i in range(len(self.data)):
            # check if any of the previously placed boxes obstruct this box
            for j in range(i):
                # check if any of the previously placed boxes obstruct this box
                if self.check_obstructed(self.data[i], self.data[j]):
                    return True, self.data[i], self.data[j]
        return False, None, None

    def criterion_volume(self):
        (
            total_min_x,
            total_min_y,
            total_min_z,
            total_max_x,
            total_max_y,
            total_max_z,
        ) = self.total_bounding_box
        total_volume = (
            (total_max_x - total_min_x)
            * (total_max_y - total_min_y)
            * (total_max_z - total_min_z)
        )
        percentage_volume = self.sum_volumes / total_volume

        return self.sum_volumes, total_volume, percentage_volume

    def criterion_support(self):
        # the following code assumes that the placement passed intersection and availability validation

        # sort the data in ascending order of posZ
        sorted_data = sorted(self.data, key=lambda x: x["posZ"])
        # empty array of the boxes, which are confirmed to be supported
        supported_boxes = []
        for box in sorted_data:
            # if all the boxes are supported exit the loop earlier
            if len(supported_boxes) == len(sorted_data):
                return True, None

            # check every box lower than the one is question of they support it
            min_x, min_y, min_z, max_x, max_y, max_z = self.bounding_box(box)
            i = 0
            total_area = 0
            if min_z > 5:
                while sorted_data[i]["posZ"] < min_z:
                    supported, area = self.check_supported(box, sorted_data[i])
                    if supported:
                        total_area += area
                    # exit early if the box is supported
                    if total_area >= 0.6:
                        supported_boxes.append(box)
                        break
                    i += 1
                if total_area < 0.6:
                    return False, box
        return True, None


def validate_placemnet(filename):
    evaluator = Evaluator(filename)

    # check if there are any box intersections
    intersection, box1, box2 = evaluator.criterion_intersection()
    if intersection:
        print(
            "Intersection criterion FAILED: boxes ", box1, " and ", box2, " intersect"
        )
    else:
        print("Intersection criterion PASSED: none of the boxes intersect each other")

    # check if any of the boxes obstruct each other
    obstructed, box1, box2 = evaluator.criterion_accessability()
    if obstructed:
        print("Accessibility criterion FAILED: box ", box2, " obstructs box ", box1)
    else:
        print("Accessibility criterion PASSED: none of the boxes obstruct each other")

    # check if the boxes' volume is more than half of that the container's
    sum_volumes, total_volume, percentage_volume = evaluator.criterion_volume()
    if percentage_volume > 0.5:
        print(
            "Volume criterion PASSED: sum of volumes =",
            sum_volumes,
            ", total volume =",
            total_volume,
            ", percentage =",
            percentage_volume,
        )
    else:
        print(
            "Volume criterion FAILED: sum of volumes =",
            sum_volumes,
            ", total volume =",
            total_volume,
            ", percentage =",
            percentage_volume,
        )

    # check if all of the boxes are supported
    supported, box = evaluator.criterion_support()
    if supported:
        print("Support criterion PASSED: every box is supported")
    else:
        print("Support criterion FAILED: box ", box, " is not supported enough")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <csv_file_name>")
    else:
        validate_placemnet(sys.argv[1])
