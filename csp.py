from typing import Generic, TypeVar
from queue import Queue
import sys
import time
import copy

T = TypeVar('T')
R = TypeVar('R')

class Constraint(Generic[T, R]):
    def __init__(self, vars):
        self.vars = vars

class ConsConstraint(Constraint[str, str]):
    def __init__(self, nurse, idx):
        super().__init__(nurse)
        self.nurse = nurse
        self.idx = idx

    def valid(self, assignment, record_nurses, record_days):
        total = len(record_nurses[self.idx])
        for i in range(total-1):
            if (assignment[self.nurse[i]] == "M" and assignment[self.nurse[i+1]] == "M"):
                return False
            if (assignment[self.nurse[i]] == "E" and assignment[self.nurse[i+1]] == "M"):
                return False
        return True

class RestConstraint(Constraint[str, str]):
    def __init__(self, nurse, idx):
        super().__init__(nurse)
        self.nurse = nurse
        self.idx = idx

    def valid(self, assignment, record_nurses, record_days):
        total = len(record_nurses[self.idx])
        if total%7 != 0:
            return True
        if (total%7 == 0):
            for i in range(total-7, total):
                if (assignment[self.nurse[i]] == "R"):
                    return True
        return False

class ShiftConstraint(Constraint[str, str]):
    def __init__(self, Shift, m, a, e, idx):
        super().__init__(Shift)
        self.Shift = Shift
        self.m = m
        self.a = a
        self.e = e
        self.idx = idx

    def valid(self, assignment, record_nurses, record_days):
        countM = 0
        countA = 0
        countE = 0
        for i in range(len(record_days[self.idx])):
            s = assignment[record_days[self.idx][i]]
            if (s == "M"): 
                countM += 1
            elif (s == "A"):
                countA += 1
            elif (s == "E"):
                countE += 1
        if (countM > self.m):
            return False
        if (countA > self.a):
            return False
        if (countE > self.e):
            return False
        if (len(record_days[self.idx]) == len(self.Shift) and countM == self.m and countA == self.a and countE == self.e):
            return True
        if (len(record_days[self.idx]) < len(self.Shift)):
            return True
        return False


class CSP(Generic[T, R]):
    def __init__(self, vars, domain, record_nurses, record_days, NumNurses, Days, m_num, a_num, e_num, best, best_weight, count):
        self.NumNurses = NumNurses
        self.Days = Days
        self.m_num = m_num
        self.a_num = a_num
        self.e_num = e_num
        self.record_nurses = record_nurses
        self.record_days = record_days
        self.vars = vars
        self.domain = domain
        self.constraints = {}
        self.best = {}
        self.best_weight = 0
        for var in self.vars:
            self.constraints[var] = []
    
    def check_consistency(self, assignment, var):
        for constraint in self.constraints[var]:
            if not constraint.valid(assignment, self.record_nurses, self.record_days):
                return False
        return True

    def add_constraint(self, constraint):
        for var in constraint.vars:
            self.constraints[var].append(constraint)

    def AddNeighbours(self, q, my_var):
        w = my_var[1:].split("_")
        # for i in range(self.NumNurses):
        #     if (i != int(w[0])):
        #         v = "N"+str(i)+"_"+w[1]
        #         q.put(v,my_var)
        for i in range(self.Days):
            if (i != int(w[1])):
                v = "N"+w[0]+"_"+str(i)
                q.put((v,my_var))
        return q

    def revise(self, var1, var2, inf):
        revised = False
        D1 = inf[var1]
        D2 = inf[var2]
        w1 = var1[1:].split("_")
        w2 = var2[1:].split("_")
        if (int(w1[0]) == int(w2[0])):
            if (int(w1[1])+1 == int(w2[1])):
                for x in D1:
                    if (x == "M" or x == "E"):
                        if "A" in D2 or "E" in D2:
                            continue
                        else:
                            D1.remove(x)
                            revised = True
            elif (int(w1[1]) == int(w2[1])+1):
                for x in D1:
                    if (x == "M"):
                        if "A" in D2:
                            continue
                        else:
                            D1.remove(x)
                            revised = True
        inf[var1] = D1
        return (revised, inf)


    def inference(self, assignment, dom, my_var):
        inf = dom
        for index, (key, value) in enumerate(assignment.items()):
            inf[key] = [value]
        q = Queue(maxsize=-1)
        q = self.AddNeighbours(q,my_var)
        while(q.empty() == False):
            (var1, var2) = q.get()
            (revised, inf) = self.revise(var1, var2, inf)
            if (revised):
                if (len(inf[var1]) == 0): return (False, inf)
                q = self.AddNeighbours(q, var1)
        return (True, inf)

    def backtrack_search(self, assignment, dom):
        print(dom)
        if len(assignment) == len(self.vars):
            return assignment

        temp = []
        for var in self.vars:
            if var not in assignment:
                temp.append(var)

        new_var = temp[0]
        w = new_var[1:].split("_")
        self.record_nurses[int(w[0])].append(new_var)
        self.record_days[int(w[1])].append(new_var)
        for data in dom[new_var]:
            assignment[new_var] = data
            if self.check_consistency(assignment, new_var):
                (t, inferences) = self.inference(assignment, dom, new_var)
                if t == True:
                    ans = self.backtrack_search(assignment, inferences)
                    if ans != None: return ans
            del assignment[new_var]
        self.record_nurses[int(w[0])].remove(new_var)
        self.record_days[int(w[1])].remove(new_var)
        return None

    def backtrack(self, assignment, timer):
        if time.time() - timer >= T - 1:
            return self.best
        
        if len(assignment) == len(self.vars):
            weight = 1
            for nurse in range(S):
                for variable in self.record_nurses[nurse]:
                    if assignment[variable] == "M" or assignment[variable] == "E":
                        weight *= 2
            if weight > self.best_weight:
                self.best = copy.deepcopy(assignment)
                self.best_weight = weight
            return None

        temp = []
        for var in self.vars:
            if var not in assignment:
                temp.append(var)

        new_var = temp[0]
        w = new_var[1:].split("_")
        self.record_nurses[int(w[0])].append(new_var)
        self.record_days[int(w[1])].append(new_var)
        for data in self.domain[new_var]:
            assignment[new_var] = data
            if self.check_consistency(assignment, new_var):
                ans = self.backtrack(assignment, timer)
                if ans != None: return ans
            del assignment[new_var]
        self.record_nurses[int(w[0])].remove(new_var)
        self.record_days[int(w[1])].remove(new_var)
        return None



if __name__ == "__main__":
    with open(sys.argv[1], 'r') as file:
        l = len(file.readline().split(","))
        if l == 5:
            for line in file:
                words = line.split(",")
                N = int(words[0])
                D = int(words[1])
                m = int(words[2])
                a = int(words[3])
                e = int(words[4])
                timer = time.time()
                record_nurses = [[] for i in range(N)]
                record_days = [[] for i in range(D)]
                vars = []
                for j in range(D):
                    for i in range(N):
                        vars.append("N"+str(i)+"_"+str(j))
                domain = {}
                for var in vars:
                    domain[var] = ["M", "A", "E", "R"]
                csp = CSP(vars, domain, record_nurses, record_days, N, D, m, a, e)
                for i in range(N):
                    nurse = ["N"+str(i)+"_"+str(j) for j in range(D)]
                    csp.add_constraint(ConsConstraint(nurse, i))
                for i in range(D):
                    day = ["N"+str(j)+"_"+str(i) for j in range(N)]
                    csp.add_constraint(ShiftConstraint(day, m, a, e, i))
                if (D >= 7):
                    for i in range(N):
                        nurse = ["N"+str(i)+"_"+str(j) for j in range(D)]
                        csp.add_constraint(RestConstraint(nurse, i))
                solution = csp.backtrack_search({}, domain)
                timer = time.time() - timer
                if solution is None:
                    print("NO-SOLUTION")
                else:
                    print(solution)
        else:
            for line in file:
                words = line.split(",")
                N = int(words[0])
                D = int(words[1])
                m = int(words[2])
                a = int(words[3])
                e = int(words[4])
                S = int(words[5])
                T = int(words[6])
                record_nurses = [[] for i in range(N)]
                record_days = [[] for i in range(D)]
                vars = []
                for j in range(D):
                    for i in range(N):
                        vars.append("N"+str(i)+"_"+str(j))
                domain = {}
                for var in vars:
                    domain[var] = ["M", "E", "A", "R"]
                csp = CSP(vars, domain, record_nurses, record_days, N, D, m, a, e, {}, 0, 0)
                for i in range(N):
                    nurse = ["N"+str(i)+"_"+str(j) for j in range(D)]
                    csp.add_constraint(ConsConstraint(nurse, i))
                for i in range(D):
                    day = ["N"+str(j)+"_"+str(i) for j in range(N)]
                    csp.add_constraint(ShiftConstraint(day, m, a, e, i))
                if (D >= 7):
                    for i in range(N):
                        nurse = ["N"+str(i)+"_"+str(j) for j in range(D)]
                        csp.add_constraint(RestConstraint(nurse, i))
                solution = csp.backtrack({}, time.time())
                if csp.best is None:
                    print("NO-SOLUTION")
                else:
                    print(csp.best)
