# src/qap_solver.py
from dimod import Binary, ConstrainedQuadraticModel, quicksum
from dwave.system import LeapHybridCQMSampler
import numpy as np


def find_reallocation_costs(A1, D):
    """
    Compute a reallocation cost matrix from a reference assignment (A1) and the distance matrix (D).
    For each row in A1, finds the first column where A1[i,j]=1 and computes the difference between
    that distance and the distance in every column.
    """
    A3 = np.zeros_like(D, dtype=float)
    for i in range(A1.shape[0]):
        ref_index = np.where(A1[i] == 1)[0]
        if len(ref_index) > 0:
            ref_index = ref_index[0]
            ref_value = D[i, ref_index]
            for j in range(A1.shape[1]):
                if j != ref_index:
                    A3[i, j] = abs(ref_value - D[i, j])
    return A3


def build_time_qap_cqm(D: np.ndarray, F_time: list, lambda_move: float = 0.0, R_time: list = None) -> ConstrainedQuadraticModel:
    """
    Build a time-dependent QAP model with optional reallocation costs and transition (relocation) cost.
    Args:
        D (np.ndarray): Fixed distance matrix (N×N).
        F_time (list): List of T flow matrices (each N×N).
        lambda_move (float): Weight for the transition cost between time steps.
        R_time (list): Optional list of previous assignment matrices (each N×N) used to compute reallocation cost.
    Returns:
        ConstrainedQuadraticModel: The time-dependent QAP model.
    """
    T = len(F_time)
    N = D.shape[0]
    cqm = ConstrainedQuadraticModel()
   
    # Create binary variables x_{j,m,t} for every facility j, location m, and time step t
    x = {}
    for t in range(T):
        for j in range(N):
            for m in range(N):
                x[(j, m, t)] = Binary(f"x_{j}_{m}_{t}")
   
    # Add strict assignment constraints with high penalty values
    for t in range(T):
        # Each facility must be assigned to exactly one location
        for j in range(N):
            facility_constraint = quicksum(x[(j, m, t)] for m in range(N)) == 1
            cqm.add_constraint(facility_constraint, label=f"facility_{j}_t{t}", penalty=1000.0)
       
        # Each location must have exactly one facility
        for m in range(N):
            location_constraint = quicksum(x[(j, m, t)] for j in range(N)) == 1
            cqm.add_constraint(location_constraint, label=f"location_{m}_t{t}", penalty=1000.0)
   
    # Build the objective
    obj = 0
    # Standard QAP cost at each time step
    for t in range(T):
        F = F_time[t]
        for j in range(N):
            for k in range(N):
                for m in range(N):
                    for n in range(N):
                        if j != k and m != n:  # Avoid self-loops
                            term = F[j, k] * D[m, n] * x[(j, m, t)] * x[(k, n, t)]
                            obj += term
   
    # Add reallocation (transition) costs between consecutive time steps
    if lambda_move > 0 and T > 1:
        for t in range(1, T):
            for j in range(N):
                for m in range(N):
                    for n in range(N):
                        if m != n:  # Only penalize actual moves
                            move_cost = D[m, n] * lambda_move
                            obj += move_cost * x[(j, m, t-1)] * x[(j, n, t)]
   
    cqm.set_objective(obj)
    return cqm


def process_model_output_time(sampleset, T, N):
    """
    Process the output from a time-dependent QAP model with additional validation.
    Returns a list of T assignment matrices (each N×N) indicating the facility-to-location assignments.
    """
    assignments = []
    sample = sampleset.first.sample
   
    # Process assignments time step by time step
    for t in range(T):
        assignment = np.zeros((N, N), dtype=int)
       
        # Fill in assignments for this time step
        for j in range(N):
            for m in range(N):
                key = f"x_{j}_{m}_{t}"
                if key in sample:
                    value = int(round(sample[key]))
                    assignment[j, m] = value
       
        # Validate assignment matrix
        row_sums = np.sum(assignment, axis=1)
        col_sums = np.sum(assignment, axis=0)
       
        # If any constraints are violated, apply correction
        if not (np.all(row_sums == 1) and np.all(col_sums == 1)):
            # Use Hungarian algorithm for correction
            from scipy.optimize import linear_sum_assignment
            cost_matrix = -assignment  # Convert to cost minimization
            row_ind, col_ind = linear_sum_assignment(cost_matrix)
           
            # Create corrected assignment matrix
            corrected_assignment = np.zeros_like(assignment)
            corrected_assignment[row_ind, col_ind] = 1
            assignment = corrected_assignment
       
        assignments.append(assignment)
   
    return assignments


def run_time_qap_cqm(cqm: ConstrainedQuadraticModel, T: int, N: int, time_limit: int = 60):
    """
    Solve the time-dependent QAP model using D-Wave's Leap Hybrid CQM Solver with extended time limit.
    Returns:
        List of T assignment matrices.
    """
    sampler = LeapHybridCQMSampler()
    sampleset = sampler.sample_cqm(cqm, time_limit=time_limit)
    return process_model_output_time(sampleset, T, N)



