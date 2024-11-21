# mujin_interview

The solution for the task is located in main.py

```
python3 main.py <csv_file_name>
```

Let me provide some additional explanation for every validation check.

## Intersection
First, the algorithm finds the smallest dimensions among the presented boxes and creates a new system of coordinates with these dimensions as units. Thus, the whole container is divided into cells, and each cell contains 0, 1, or multiple boxes (or rather parts of them). Then the algorithm iterates through every cell and checks if any of the boxes, which take space in a given cell intersect each other. This way the algorithm doesn't have to check intersection of a box with every other (which would make the complexity O(n^2)), but only with some of its neighbours. There are more cells then boxes, but the anount of checks performed saves the computational cost in scale and in reasonable cases.

## Accessibility
For every box the algorithm checks if its projection on xy plane overlaps with any of the previous boxes, which are also higher, than the box in question. 

## Volume
The algorithm obtains the bounding box of all the placed boxes during data initialization and compares it to the sum of volumes of each individual box. THe algorithm assuems, that there are no intersections of the boxes. If there are intersection validation would fail anyway, but volume validation would count the overlap twice.

## Support
The algorithm assumes that intersection and accessibility validations were passed, so that it can reorder the data in the ascending order of posZ. This way, for every box the algorithm checks every box, which has posZ smaller then the lowest part of the box in question. I worked under the assumption, that there are no boxes with dimensions less than 14, so only 1 box can support the same box at the same point in xy plane. This way, the algorithm searches for boxes, which projection on xy axis overlaps with that of the box under consideration and keep track of its supported area. If it gets more than 60% the search terminates early, but if it finished - it mean that the box isn't supported enough.