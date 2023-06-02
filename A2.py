from typing import Generic, TypeVar
from queue import Queue
import sys
import time
import copy
import json

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
    def __init__(self, vars, domain, record_nurses, record_days, NumNurses, Days, m_num, a_num, e_num):
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

    def valid_ass(self, assignment):
        for var in self.vars:
            for constraint in self.constraints[var]:
                if not constraint.valid(assignment, self.record_nurses, self.record_days):
                    return False
        return True

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
            # Rostering with Constraints
            soln_list = []
            for line in file:
                words = line.split(",")
                N = int(words[0])
                D = int(words[1])
                m = int(words[2])
                a = int(words[3])
                e = int(words[4])
                r = N - m - a - e
                # Generate CSP and constraints
                solution = {}
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
                # Return valid solution
                if r >= 0 and (D < 7 or 7*r >= N) and 2*m + e <= N:
                    restDays = {}
                    count = 0
                    nurses = [i for i in range(N)]
                    assignment = ["M"]*m + ["E"]*e + ["A"]*a + ["R"]*r
                    variable = []
                    for i in range(D):
                        if count%7 == 0:
                            count = 0
                            for k in range(N):
                                restDays[k] = 0
                        restDays = {k: v for k, v in sorted(restDays.items(), key = lambda item: item[1])}
                        if i != 0:
                            nurses_prev = copy.deepcopy(nurses)
                            nurses = [0 for i in range(N)]
                            rest = []
                            count2 = 0
                            count1 = 0
                            for key in restDays.keys():
                                rest.append(key)
                            for k in range(m+e):
                                nurses[m+k] += nurses_prev[k]
                                if m+k >= m+a+e:
                                    restDays[nurses[m+k]] += 1
                            count2 = r - (e + a + r - m - e)
                            for k in range(len(rest)):
                                if (rest[k] == 0 or not (rest[k] in nurses)) and count2 < r:
                                    nurses[m+e+a+count2] += rest[k]
                                    restDays[rest[k]] += 1
                                    count2 += 1
                            for k in range(N):
                                if not (nurses_prev[k] in nurses):
                                    while nurses[count1] != 0:
                                        count1 += 1
                                    nurses[count1] += nurses_prev[k]
                        if i == 0:
                            for k in range(r):
                                restDays[nurses[m+e+a+k]] += 1
                        for j in range(N):
                            solution["N"+str(nurses[j])+"_"+str(i)] = assignment[j]
                            variable.append("N"+str(nurses[j])+"_"+str(i))
                        count += 1
                soln_list.append(solution)
        else:
            soln_list = []
            for line in file:
                words = line.split(",")
                N = int(words[0])
                D = int(words[1])
                m = int(words[2])
                a = int(words[3])
                e = int(words[4])
                S = int(words[5])
                T = int(words[6])
                r = N - m - a - e
                # Generate CSP and constraints
                solution = {}
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
                # Return valid solution
                if r>=0 and (D < 7 or 7*r >= N) and 2*m + e <= N:
                    restDays = {}
                    count = 0
                    nurses = [i for i in range(N)]
                    assignment = ["E"]*e + ["M"]*m + ["A"]*a + ["R"]*r
                    variable = []
                    for i in range(D):
                        if count%7 == 0:
                            count = 0
                            for k in range(N):
                                restDays[k] = 0
                        restDays = {k: v for k, v in sorted(restDays.items(), key = lambda item: item[1])}
                        if i != 0:
                            nurses_prev = copy.deepcopy(nurses)
                            nurses = [0 for i in range(N)]
                            rest = []
                            count2 = 0
                            count1 = 0
                            for key in restDays.keys():
                                rest.append(key)
                            for k in range(m+e):
                                nurses[m+k] += nurses_prev[k]
                                if m+k >= m+a+e:
                                    restDays[nurses[m+k]] += 1
                            count2 = r - (e + a + r - m - e)
                            for k in range(len(rest)):
                                if (rest[k] == 0 or not (rest[k] in nurses)) and count2 < r:
                                    nurses[m+e+a+count2] += rest[k]
                                    restDays[rest[k]] += 1
                                    count2 += 1
                            for k in range(N):
                                if not (nurses_prev[k] in nurses):
                                    while nurses[count1] != 0:
                                        count1 += 1
                                    nurses[count1] += nurses_prev[k]
                        if i == 0:
                            for k in range(r):
                                restDays[nurses[m+e+a+k]] += 1
                        for j in range(N):
                            solution["N"+str(nurses[j])+"_"+str(i)] = assignment[j]
                            variable.append("N"+str(nurses[j])+"_"+str(i))
                        count += 1
                soln_list.append(solution)
                weight = 0
                for nurse in range(S):
                    for day in range(D):
                        if solution["N" + str(nurse) + "_" + str(day)] == "M" or solution["N" + str(nurse) + "_" + str(day)] == "E":
                            weight += 1
                print(weight)
        with open("solution.json" , 'w') as file:
            for d in soln_list:
                d = {k: v for k, v in sorted(d.items(), key = lambda item: item[0])}
                json.dump(d,file)
                file.write("\n")
