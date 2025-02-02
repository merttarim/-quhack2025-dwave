# demo_callbacks.py
from dash import html, callback, Input, Output, State
import numpy as np
from math import ceil
import sys
import traceback


# Import the solver functions from the src folder.
from src import qap_solver
from demo_configs import QAP_DISTANCE


def update_flow_matrix(flow_matrix, timestep, update_amt=3.0):
    """
    Update flow matrix based on fire probability derived from joint drought probabilities.
   
    Args:
        flow_matrix (np.ndarray): Current flow matrix
        timestep (int): Current timestep (1-based indexing)
        update_amt (float): Amount to add to flow values when fire probability threshold is met
       
    Returns:
        np.ndarray: Updated, symmetric flow matrix
    """
    # Joint drought probabilities between consecutive months (t and t+1)
    joint_drought_probabilities = {
        (1, 2): 0.44,  # nov - dec
        (2, 3): 0.35,  # dec - jan
        (3, 4): 0.30,  # jan - feb
        (4, 5): 0.30,  # feb - march
    }


    fire_prob_ranges = {
        (1, 2): (0.48, 0.55),  # fire prob range for timesteps 1-2
        (2, 3): (0.35, 0.45),  # fire prob range for timesteps 2-3
        (3, 4): (0.26, 0.32),
        (4, 5): (0.26, 0.32),
    }


    # Define indices for resource types
    FIREFIGHTERS = 0
    EVACUATION = 1
    WATER = 2
    FIRST_RESP = 4


    # Create copy of flow matrix to update
    new_flow_matrix = flow_matrix.copy()


    timestep_pair = (timestep, timestep + 1)
    current_joint_prob = joint_drought_probabilities.get(timestep_pair, 0.3)
   
    # Get fire probability range for current timestep pair
    fire_prob_min, fire_prob_max = fire_prob_ranges.get(timestep_pair, (0.25, 0.35))
   
    # Calculate dynamic scaling factor and base probability for current timestep
    scaling_factor = (fire_prob_max - fire_prob_min) / current_joint_prob if current_joint_prob > 0 else 0
    base_prob = fire_prob_min - (current_joint_prob * scaling_factor)
   
    # Calculate fire probability based on current joint drought probability
    p_fire = current_joint_prob * scaling_factor + base_prob
   
    # Add small random variation within 10% of the range for current timestep
    variation_range = (fire_prob_max - fire_prob_min) * 0.1
    p_fire += np.random.uniform(-variation_range, variation_range)
   
    # Ensure fire probability stays within the specified range
    p_fire = np.clip(p_fire, fire_prob_min, fire_prob_max)
   
    # Update flows based on fire probability thresholds
    HIGH_FIRE_THRESHOLD = 0.45  # Above this, prioritize firefighters and water
    LOW_FIRE_THRESHOLD = 0.30   # Below this, prioritize evacuation supplies
   
    for i in range(flow_matrix.shape[0]):
        for j in range(flow_matrix.shape[1]):
            if flow_matrix[i, j] != 0:  # Only update existing flows
                if p_fire >= HIGH_FIRE_THRESHOLD:
                    # High fire probability: increase firefighter and water-related flows
                    if (i == FIREFIGHTERS and j == WATER):
                        if np.random.random() <= p_fire:
                            new_flow_matrix[i, j] += update_amt * 1.5  # 50% more for critical resources
                elif p_fire <= LOW_FIRE_THRESHOLD:
                    # Low fire probability: increase evacuation-related flows
                    if (i == FIRST_RESP or i == EVACUATION):
                        if np.random.random() <= (1 - p_fire):  # Higher chance when fire probability is lower
                            new_flow_matrix[i, j] += update_amt * 1.2  # 20% more for evacuation
                else:
                    # Moderate fire probability: balanced updates
                    if np.random.random() <= p_fire:
                        new_flow_matrix[i, j] += update_amt
                       
    # Re-symmetrize the matrix by averaging with its transpose
    new_flow_matrix = (new_flow_matrix + new_flow_matrix.T) / 2
    return new_flow_matrix


def generate_random_flow_matrices(T, N):
    """
    Generate T flow matrices (each N×N) with random values that are updated based on fire risk.
    Instead of generating entirely new random matrices at each timestep,
    the initial matrix is updated for subsequent timesteps.
    """
    flows = []
    # Generate the initial random flow matrix and ensure it's symmetric
    initial_F = np.random.randint(1, 21, size=(N, N))
    np.fill_diagonal(initial_F, 0)
    initial_F = (initial_F + initial_F.T) // 2
    flows.append(initial_F)
   
    # For each subsequent timestep, update the previous flow matrix
    for t in range(1, T):
        updated_F = update_flow_matrix(flows[-1], timestep=t)
        flows.append(updated_F)
    return flows


def create_assignment_table(assignment):
    """
    Create an HTML table for the assignment matrix with clear formatting.
    """
    N = len(assignment)
    return html.Table(
        [
            # Header row
            html.Tr(
                [html.Th("Facility/Location", style={'backgroundColor': '#f0f0f0', 'padding': '10px'})] +
                [html.Th(f"Location {i+1}", style={'backgroundColor': '#f0f0f0', 'padding': '10px'}) for i in range(N)]
            )
        ] +
        # Data rows
        [
            html.Tr(
                [html.Td(
                    f"{'First Responders' if i % 2 == 0 else 'Supplies'} {ceil((i+1)/2)}",
                    style={'fontWeight': 'bold', 'padding': '10px'}
                )] +
                [
                    html.Td(
                        "✓" if assignment[i][j] == 1 else "-",
                        style={
                            'padding': '10px',
                            'backgroundColor': '#e6f3ff' if assignment[i][j] == 1 else 'white'
                        }
                    )
                    for j in range(N)
                ]
            )
            for i in range(N)
        ],
        style={
            'borderCollapse': 'collapse',
            'border': '2px solid #ddd',
            'margin': '20px auto',
            'width': '80%',
            'maxWidth': '800px'
        }
    )


@callback(
    Output("output-container", "children"),
    Input("run-button", "n_clicks"),
    State("time-steps-slider", "value"),
    State("lambda-slider", "value"),
    prevent_initial_call=True
)
def run_time_qap(n_clicks, time_steps, lambda_val):
    if n_clicks is None or n_clicks == 0:
        return html.Div("Click 'Run Optimization' to start.", style={'fontSize': '16px'})
    try:
        print(f"[DEBUG] Running optimization with T={time_steps}, λ={lambda_val}", file=sys.stderr)
        D = QAP_DISTANCE
        N = D.shape[0]
        T = time_steps
       
        # Generate T symmetric flow matrices with updated probabilities.
        F_time = generate_random_flow_matrices(T, N)
        print("[DEBUG] Generated flow matrices:", file=sys.stderr)
        for t, F in enumerate(F_time):
            print(f"[DEBUG] Flow matrix at time step {t+1}:\n{F}\n", file=sys.stderr)
       
        # Build and run the time-dependent QAP model.
        cqm = qap_solver.build_time_qap_cqm(D, F_time, lambda_move=lambda_val)
        print("[DEBUG] Built CQM model.", file=sys.stderr)
        assignments = qap_solver.run_time_qap_cqm(cqm, T, N, time_limit=60)
        if not assignments or len(assignments) == 0:
            return html.Div("No assignments were produced.", style={'color': 'red', 'fontSize': '16px'})
       
        # Print out every assignment matrix for debugging.
        for t, assignment in enumerate(assignments):
            print(f"[DEBUG] Assignment matrix at time step {t+1}:\n{assignment}\n", file=sys.stderr)
       
        first_assignment = assignments[0]
        # Debug: Print row and column sums for the first assignment
        row_sums = np.sum(first_assignment, axis=1)
        col_sums = np.sum(first_assignment, axis=0)
        print(f"[DEBUG] First assignment - row sums: {row_sums}, column sums: {col_sums}", file=sys.stderr)
     
        table = create_assignment_table(first_assignment)
       
        return html.Div(
            [
                html.H2("Facility-Location Assignment (Time Step 1)", style={'textAlign': 'center', 'margin': '20px 0'}),
                html.P(f"Optimization Parameters: Time Steps = {T}, λ = {lambda_val}",
                       style={'textAlign': 'center', 'marginBottom': '20px'}),
                table
            ],
            style={
                'margin': '20px',
                'padding': '20px',
                'border': '1px solid #ddd',
                'borderRadius': '8px',
                'backgroundColor': 'white'
            }
        )
    except Exception as e:
        err_msg = f"Error in callback: {str(e)}\n" + traceback.format_exc()
        print(err_msg, file=sys.stderr)
        return html.Div(
            [
                html.H3("Error", style={'color': 'red', 'textAlign': 'center'}),
                html.Pre(err_msg)
            ],
            style={'margin': '20px', 'padding': '20px', 'border': '1px solid red'}
        )
