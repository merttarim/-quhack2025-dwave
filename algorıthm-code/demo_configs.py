# demo_configs.py
import numpy as np


APP_TITLE = "QAP Solver Demo"
MAIN_HEADER = "Quadratic Assignment Problem Solver"
DESCRIPTION = (
    "This demo solves a time-dependent Quadratic Assignment Problem (QAP) using D-Wave's CQM Solver. "
    "Flow matrices vary over time and a fixed distance matrix is used to find the optimal assignment of facilities to locations. "
    "Transition costs are applied to penalize facility moves."
)


table_size = 4  # You can change the table size as needed


np.random.seed(42)


# Generate a symmetric flow matrix for the static demo (not used in time-dependent mode).
QAP_FLOW = np.random.randint(1, 21, size=(table_size, table_size))
np.fill_diagonal(QAP_FLOW, 0)
QAP_FLOW = (QAP_FLOW + QAP_FLOW.T) // 2


# Generate a symmetric distance matrix.
QAP_DISTANCE = np.random.randint(1, 51, size=(table_size, table_size))
np.fill_diagonal(QAP_DISTANCE, 0)
QAP_DISTANCE = (QAP_DISTANCE + QAP_DISTANCE.T) // 2
