# mujin_interview

The solution for the task is located in main.py

The algorithm checks for intersections in a convoluted way, so let me explain it here. 
First, the algorithm finds the smallest dimensions among the presented boxes and creates a new system of coordinates with these dimensions as units. Thus, the whole container is divided into cells, and every box can be described by the cells it occupies. Then the algorithm iterates through every cell and check if any of the boxes, which take space in a given cell intersect each other. This way the algorithm doesn't have to check intersection of a box with every other (which would make the complexity O(n^2)), but only with some of its neighbours (there are more cells then boxes, but the anount of checks performed saves the computational cost in scale).