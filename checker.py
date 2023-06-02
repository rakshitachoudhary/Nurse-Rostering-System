import argparse
import json
import csv

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("solution", type=str)
    parser.add_argument("input", type=str)
    return parser.parse_args()


def get_nd(var: str):
    var = var[1:]
    [n, d] = var.split('_')
    return int(n), int(d)



def check(solution: dict, M: int, E: int, A: int):
    if len(solution) == 0:
        return None
    N = D = 0
    for var in solution.keys():
        n, d = get_nd(var)
        N = max(N, n)
        D = max(D, d)
    N += 1
    D += 1
    for n in range(N):
        for week in range(D // 7):
            if all(solution[f"N{n}_{d}"] != 'R' for d in range(7 * week, 7 * (week + 1))):
                print(1)
                return False
    m = sum(solution[f"N{n}_0"] == 'M' for n in range(N))
    a = sum(solution[f"N{n}_0"] == 'A' for n in range(N))
    e = sum(solution[f"N{n}_0"] == 'E' for n in range(N))
    for d in range(1, D):
        if m != sum(solution[f"N{n}_{d}"] == 'M' for n in range(N)):
            print(2)
            return False
        if a != sum(solution[f"N{n}_{d}"] == 'A' for n in range(N)):
            print(2)
            return False
        if e != sum(solution[f"N{n}_{d}"] == 'E' for n in range(N)):
            print(2)
            return False

    for n in range(N):
        for d in range(D - 1):
            if solution[f"N{n}_{d}"] in ('M', 'E') and solution[f"N{n}_{d + 1}"] == 'M':
                    print(3)
                    return False
    return (m, a, e) == (M, A, E)


if __name__ == "__main__":
    args = parse_args()
    with open(args.solution) as f:
        with open(args.input, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for line, row in zip(f, reader):
                count += 1
                ret = check(json.loads(line), int(row['m']), int(row['e']), int(row['a']))
                if ret is False:
                    print(count)
                    assert False
