Time-Dependent QAP Solver Demo
Overview
This demo application shows how to solve a Time-Dependent Quadratic Assignment Problem (QAP) using D-Wave’s hybrid solver. In plain language, we are trying to decide which facility (like a fire station or supply depot) should be assigned to which location over several time steps. The assignments change over time based on certain “flow” values that represent how much one facility might need to interact with another. We also add extra costs if facilities move between locations over time.

The application is built with Dash (a Python web framework) and uses D-Wave’s Leap Hybrid Constrained Quadratic Model (CQM) Solver to find the best assignment. You can change two main parameters:

Number of Time Steps: How many different moments in time you want to plan for.
Relocation Cost Weight (λ): A number that makes moving a facility between locations more or less expensive.
When you run the app, you’ll see an interactive webpage where you choose your parameters and click “Run Optimization.” The app then shows you a table of assignments (for the first time step) and prints extra debugging information (like the flow matrices and binary assignment matrices) in the terminal.

How It Works – Step by Step
1. Creating Flow Matrices
What is a Flow Matrix?
A flow matrix is like a table with numbers that show how much “interaction” or “flow” there is between different facilities. For example, if one facility needs to send supplies to another, the number in the matrix tells us how strong that connection is.

Random Generation and Updates:

We start by generating a completely random, symmetric flow matrix (i.e., the value from facility A to facility B is the same as from B to A).
For each subsequent time step, we do not create an entirely new random matrix. Instead, we update the previous one using a function called update_flow_matrix.
This function simulates “fire risk” by calculating a fire probability based on pre-set drought probabilities and fire probability ranges.
Depending on whether the fire probability is high, low, or moderate, we increase the flow values for certain types of facilities (like increasing flow between firefighters and water during high fire risk).
Symmetry Check:
At the end of the update, we re-make sure the matrix is symmetric by averaging the matrix with its transpose.

2. Building the QAP Model
Decision Variables:
The model creates binary decision variables (x_j_m_t) for every facility j, location m, and time step t. A value of 1 means facility j is assigned to location m at time t, and 0 means it is not.

Assignment Constraints:
The model forces each facility to be assigned to exactly one location and each location to have exactly one facility. We do this by adding constraints that sum up the decision variables for each facility and each location.

Objective Function (Cost Calculation):

At each time step, we calculate a cost based on the flow values and the distances between locations.
For every pair of facilities and every pair of locations, if facility j is assigned to location m and facility k is assigned to location n, then we add a cost that is the product of the flow between j and k and the distance between m and n.
Additionally, if a facility moves from one location to another between time steps, a relocation (or transition) cost is added. This cost is weighted by the λ parameter that you choose.
3. Solving the QAP Model
Using D-Wave’s Solver:
The constructed model (with variables, constraints, and objective) is sent to D-Wave’s Leap Hybrid CQM Solver. This solver is “hybrid” because it uses both classical and quantum computing techniques.

Getting the Solution:
The solver returns a set of binary assignment matrices (one for each time step). Each matrix tells us which facility goes to which location at that particular time step.

4. Displaying and Debugging Results
Web Interface:
The app displays an HTML table for the first time step’s assignment. The table shows “✓” for an assignment and “–” where there is no assignment.

Terminal Debugging:
For each time step, the terminal prints:

The symmetric flow matrix (after random generation or updating).
The binary assignment matrix (the result of the optimization).
The row and column sums of the assignment matrix (to check that each facility and location is used exactly once).
This extra debugging information helps ensure that the algorithm is working correctly at every step.

Code Structure
bash
Copy
qap-solver-demo/
├── src/
│   └── qap_solver.py         # Contains the core QAP model building and solving functions.
├── demo_configs.py           # Contains configuration variables and example distance/flow matrices.
├── demo_interface.py         # Contains the layout and UI components built with Dash.
├── demo_callbacks.py         # Contains the functions that respond to user actions and run the optimization.
├── app.py                    # Main entry point that starts the Dash web server.
├── requirements.txt          # Lists the required Python packages.
└── README.md                 # This detailed explanation file.
A Quick Look at the Main Files
app.py:
Initializes the Dash app, sets the layout (using demo_interface.py), and registers callbacks (using demo_callbacks.py).

demo_interface.py:
Creates the webpage layout with sliders for the number of time steps and the relocation cost weight, plus a “Run Optimization” button and an output container.

demo_callbacks.py:

Contains the update_flow_matrix and generate_random_flow_matrices functions that handle how flow values change over time.
Builds the QAP model using these matrices and runs the solver.
Prints debugging information (the flow and assignment matrices) to the terminal.
Generates an HTML table to display the assignment for the first time step.
src/qap_solver.py:
Contains the functions to build the QAP model (with all constraints and the cost function) and to process the output from the solver.

demo_configs.py:
Contains settings and sample data like the fixed distance matrix, which is used by the QAP model.

Installation and Running the App
Prerequisites
Python 3.8 or higher
pip
Install Dependencies
Clone the repository, set up a virtual environment (optional), and install required packages:

bash
Copy
git clone https://github.com/your-repo/qap-solver-demo.git
cd qap-solver-demo
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
Running the Application
Start the app by running:

bash
Copy
python app.py
Then, open your browser and navigate to http://127.0.0.1:8051/.

How to Use the Interface
Set the Number of Time Steps:
Use the slider to choose how many time steps (different planning moments) you want. For example, choose “3” for three planning periods.

Set the Relocation Cost Weight (λ):
Adjust this slider to set how expensive it is to move a facility from one location to another between time steps.

Run Optimization:
Click the "Run Optimization" button.

The app generates random flow matrices that change over time.
It builds the QAP model with your chosen parameters.
It runs the solver and prints detailed debugging information (flow matrices and assignment matrices) in the terminal.
View Results:
The assignment for the first time step is displayed as an HTML table on the webpage. In the terminal, you will see printed matrices that show the full binary assignment for each time step.

Additional Notes
D-Wave Leap API:
The QAP solver uses D-Wave’s cloud service. Make sure you have your API credentials set up correctly.

Execution Time:
Depending on the size of the problem and the solver’s load, it may take a while to see the result.

Debugging:
The terminal output is very detailed. It prints every flow matrix and binary assignment matrix so that you can check the inner workings of the algorithm step by step.

License
This project is licensed under the MIT License.

Author
-

Acknowledgments
D-Wave Systems for providing the hybrid quantum-classical solver.
Dash for making interactive web applications easy in Python.
Thanks to all contributors and users for feedback and suggestions.
