#!/usr/bin/python
import argparse
import glob
from pathlib import Path
from cbs import CBSSolver
from mccbs import MCCBSSolver
from mccbs_ds import MCCBS_dsSolver
from independent import IndependentSolver
from prioritized import PrioritizedPlanningSolver
from visualize import Animation
from single_agent_planner import get_sum_of_cost

SOLVER = "CBS"

def print_mapf_instance(my_map, starts, goals, sizes):
    print('Start locations')
    print_locations(my_map, starts)
    print('Goal locations')
    print_locations(my_map, goals)
    print('Sizes')
    print(sizes)

def print_locations(my_map, locations):
    starts_map = [[-1 for _ in range(len(my_map[0]))] for _ in range(len(my_map))]
    for i in range(len(locations)):
        starts_map[locations[i][0]][locations[i][1]] = i
    to_print = ''
    for x in range(len(my_map)):
        for y in range(len(my_map[0])):
            if starts_map[x][y] >= 0:
                to_print += str(starts_map[x][y]) + ' '
            elif my_map[x][y]:
                to_print += '@ '
            else:
                to_print += '. '
        to_print += '\n'
    print(to_print)


def import_mapf_instance(filename):
    f = Path(filename)
    if not f.is_file():
        raise BaseException(filename + " does not exist.")
    f = open(filename, 'r')
    # first line: #rows #columns
    line = f.readline()
    rows, columns = [int(x) for x in line.split(' ')]
    rows = int(rows)
    columns = int(columns)
    # #rows lines with the map
    my_map = []
    for r in range(rows):
        line = f.readline()
        my_map.append([])
        for cell in line:
            if cell == '@':
                my_map[-1].append(True)
            elif cell == '.':
                my_map[-1].append(False)
    # #agents
    line = f.readline()
    num_agents = int(line)
    # #agents lines with the start/goal positions
    starts = []
    goals = []
    sizes = []
    for a in range(num_agents):
        line = f.readline()
        # sx, sy, gx, gy = [int(x) for x in line.split(' ')]
        size = 1
        line_arr = line.split(' ')
        for x in range(len(line_arr)):
            if x == 0:
                sx = int(line_arr[0])
            elif x == 1:
                sy = int(line_arr[1])
            elif x == 2:
                gx = int(line_arr[2])
            elif x == 3:
                gy = int(line_arr[3])
            elif x == 4:
                size = int(line_arr[4])

        starts.append((sx, sy))
        goals.append((gx, gy))
        sizes.append(size)


    f.close()
    return my_map, starts, goals, sizes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs various MAPF algorithms')
    parser.add_argument('--instance', type=str, default=None,
                        help='The name of the instance file(s)')
    parser.add_argument('--batch', action='store_true', default=False,
                        help='Use batch output instead of animation')
    parser.add_argument('--disjoint', action='store_true', default=False,
                        help='Use the disjoint splitting')
    parser.add_argument('--solver', type=str, default=SOLVER,
                        help='The solver to use (one of: {CBS,Independent,Prioritized}), defaults to ' + str(SOLVER))

    args = parser.parse_args()


    result_file = open("results.csv", "w", buffering=1)

    for file in sorted(glob.glob(args.instance)):

        print("***Import an instance***")
        my_map, starts, goals, sizes = import_mapf_instance(file)
        print_mapf_instance(my_map, starts, goals, sizes)

        if args.solver == "CBS":
            print("***Run CBS***")
            cbs = CBSSolver(my_map, starts, goals)
            paths = cbs.find_solution(args.disjoint)
        elif args.solver == "MCCBS":
            print("***Run MCCBS***")
            mccbs = MCCBSSolver(my_map, starts, goals, sizes)
            paths = mccbs.find_solution(args.disjoint)
        elif args.solver == "MCCBS_ds":
            print("***Run MCCBS(ds)***")
            mccbs_ds = MCCBS_dsSolver(my_map, starts, goals, sizes)
            paths = mccbs_ds.find_solution(args.disjoint)
        elif args.solver == "Independent":
            print("***Run Independent***")
            solver = IndependentSolver(my_map, starts, goals, sizes)
            paths = solver.find_solution()
        elif args.solver == "Prioritized":
            print("***Run Prioritized***")
            solver = PrioritizedPlanningSolver(my_map, starts, goals)
            paths = solver.find_solution()
        else:
            raise RuntimeError("Unknown solver!")

        cost = get_sum_of_cost(paths)
        # result_file.write("{}:\t{} | {}/{}\n".format(file, cost,mccbs.num_of_expanded,mccbs.num_of_generated))
        result_file.write("{},{}\n".format(file, cost))


        if not args.batch:
            print("***Test paths on a simulation***")
            animation = Animation(my_map, starts, goals, paths, sizes)
            # animation.save("output.mp4", 1.0)
            animation.show()
    result_file.close()
