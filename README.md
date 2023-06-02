# Automated-Nurse-Rostering-System

This Assignment involved solving a rostering problem using constraint-satisfaction techniques.

## Approach

Given the inputs, number of nurses (N) and number of days (D), we modeled our problem as follows: We have N*D variables representing the shift assigned to nurses on different days. These variables can take the values "M", "A", "E" and "R".

We implemented a CSP model to assign values to these variables and provide an assignment that satisfies all applied constraints. This CSP performs a backtracking search to obtain one such valid assignment. After assigning each variable we check if it is consistent with our constraints. And if at any point, this consistency fails we backtrack.
Simple backtracking search is very slow, so we optimize it further. We use the properties of our CSP to make our search faster. Firstly, we assign the values for all Day 1 variables while following all the constraints. And then for the later days, we carefully order our choices for each variable such that our choices for assignment satisfy the constraints for most cases and we backtrack a minimum number of times. We prioritize the variables to assign by the day number of variables, we proceed with increasing number of days. This gives us a valid assignment in relatively short time intervals.

For the second part of the assignment, we again use our CSP with backtracking search. In order to maximize the score of our assignment, we prioritize the M's and E's for senior nurses. While performing search, we try assigning M or E to senior nurses for as long as the constraints are satisfied. We follow the same arrangement for variable prioritization as in part 1. This gives an assignment with good, if not best score.

## How to run?
Run using `python3 csp.py <csv_filename>`

## About
Done with [Jitender-Kumar-Yadav](https://github.com/Jitender-Kumar-Yadav) as a part of the course COL333 - Introduction to Artificial Intelligence at IIT Delhi
