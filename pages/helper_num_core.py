"""
Stock Cutting Optimization Module

This module provides an optimal solution to the 1D cutting stock problem using
the Gilmore-Gomory column generation approach with blade cut length (kerf) support.

Key Features:
    - Exact optimal solution using OR-Tools CBC solver
    - Support for decimal precision using Python's Decimal type
    - Kerf (blade cut length) modeling for realistic cutting scenarios
    - Pattern generation with depth-first search enumeration

Author: Abhishek Amgain
Company: Mid South Extrusion
Date: January 2026
"""

from __future__ import annotations
from decimal import Decimal, getcontext
from typing import List, Dict, Any
from ortools.linear_solver import pywraplp


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _decimal_scale_factor(values: List[Decimal]) -> int:
    """
    Determine the optimal integer scaling factor for decimal values.
    
    This function analyzes a list of Decimal values and returns a power of 10
    that can convert all values to integers without loss of precision.
    
    Args:
        values: List of Decimal numbers to analyze
        
    Returns:
        Integer scaling factor (10^k) where k is the maximum decimal places
        
    Example:
        >>> _decimal_scale_factor([Decimal('1.25'), Decimal('2.5')])
        100  # 10^2 to handle 2 decimal places
    """
    k = 0
    for v in values:
        exp = -v.as_tuple().exponent
        if exp > k:
            k = exp
    return 10 ** k


def _generate_all_patterns(L: int, widths: List[int]) -> List[List[int]]:
    """
    Enumerate all feasible cutting patterns using depth-first search.
    
    A pattern is a valid combination of item counts that fit within the master
    length constraint. This function generates all possible patterns where:
        sum(pattern[i] * widths[i]) <= L
    
    Args:
        L: Maximum length available (scaled to integer)
        widths: List of item widths (scaled to integers)
        
    Returns:
        List of patterns, where each pattern is a list of integer counts
        
    Algorithm:
        Uses recursive DFS with pruning to efficiently explore the solution space.
        For each item, tries all feasible counts from 0 to the maximum that fits.
    """
    m = len(widths)
    patterns: List[List[int]] = []
    max_counts = [L // w for w in widths]

    def dfs(i: int, remaining: int, current: List[int]):
        """Recursive pattern enumeration with capacity tracking."""
        if i == m:
            if any(c > 0 for c in current):
                patterns.append(current.copy())
            return

        w = widths[i]
        max_c = min(max_counts[i], remaining // w)
        for c in range(max_c + 1):
            current[i] = c
            dfs(i + 1, remaining - c * w, current)
        current[i] = 0

    dfs(0, L, [0] * m)
    return patterns




# ============================================================================
# MAIN OPTIMIZATION FUNCTION
# ============================================================================

def optimize_unlimited_stock_gg(
    master_length: float,
    demands: List[Dict[str, float]],
    kerf: float = 0.25,
) -> Dict[str, Any]:
    """
    Solve the 1D cutting stock problem to optimality with kerf support.
    
    This function computes the minimum number of master cores (stock rolls) needed
    to satisfy all cutting demands, accounting for blade cut length (kerf).
    
    Args:
        master_length: Length of each master core/stock roll (in inches)
        demands: List of cutting requirements, each containing:
            - 'width': float - the size of the cut piece
            - 'quantity': int - number of pieces needed
        kerf: Blade cut length to account for between pieces (default: 0.5 inches)
        
    Returns:
        Dictionary containing:
            - cores_required: int - minimum number of master cores needed
            - total_waste: float - total unused material across all cores
            - total_waste_percent: float - waste as percentage of total material
            - cutting_plan: list - detailed cutting patterns with counts
            
    Kerf Model:
        - If a pattern produces n pieces, it requires (n-1) cuts
        - Kerf loss per core = (n-1) * kerf
        - Feasibility constraint: sum(a_i*w_i) + (n-1)*kerf <= master_length
        - Equivalent to: sum(a_i*(w_i+kerf)) <= master_length + kerf
        
    Raises:
        ValueError: If master_length <= 0, kerf < 0, or any item width > master_length
        RuntimeError: If OR-Tools solver is not available
        
    Example:
        >>> demands = [
        ...     {"width": 45.0, "quantity": 4},
        ...     {"width": 36.0, "quantity": 3},
        ... ]
        >>> result = optimize_unlimited_stock_gg(100.0, demands, kerf=0.5)
        >>> print(f"Cores needed: {result['cores_required']}")
    """
    
    # ========================================================================
    # STEP 1: INPUT VALIDATION AND PARSING
    # ========================================================================
    
    # Validate master length and kerf
    if master_length <= 0:
        raise ValueError("master_length must be > 0")
    if kerf < 0:
        raise ValueError("kerf must be >= 0")

    # Parse and validate demands
    widths_f: List[float] = []
    qty: List[int] = []
    for d in demands:
        w = float(d["width"])
        q = int(d["quantity"])
        if w <= 0:
            raise ValueError("All item widths must be > 0")
        if q < 0:
            raise ValueError("All quantities must be >= 0")
        widths_f.append(w)
        qty.append(q)

    # Handle edge case: no pieces to cut
    if sum(qty) == 0:
        return {
            "cores_required": 0,
            "total_waste": 0.0,
            "total_waste_percent": 0.0,
            "cutting_plan": [],
        }

    # ========================================================================
    # STEP 2: DECIMAL-SAFE SCALING FOR INTEGER OPTIMIZATION
    # ========================================================================
    
    # Set high precision for Decimal calculations
    getcontext().prec = 28
    
    # Convert all measurements to Decimal for exact arithmetic
    L_dec = Decimal(str(master_length))
    k_dec = Decimal(str(kerf))
    w_dec = [Decimal(str(w)) for w in widths_f]

    # Apply kerf transformation for pattern feasibility
    # Effective constraint: sum(a_i*(w_i+kerf)) <= master_length + kerf
    L_eff_dec = L_dec + k_dec
    w_eff_dec = [wd + k_dec for wd in w_dec]

    # Compute scaling factor to convert to integers
    scale = _decimal_scale_factor([L_eff_dec, k_dec] + w_eff_dec)

    # Scale all values to integers for pattern generation
    L_eff = int((L_eff_dec * scale).to_integral_value(rounding="ROUND_HALF_UP"))
    widths_eff = [int((wd * scale).to_integral_value(rounding="ROUND_HALF_UP")) for wd in w_eff_dec]

    # Also keep original scaled values for waste calculation
    L = int((L_dec * scale).to_integral_value(rounding="ROUND_HALF_UP"))
    widths = [int((wd * scale).to_integral_value(rounding="ROUND_HALF_UP")) for wd in w_dec]
    k = int((k_dec * scale).to_integral_value(rounding="ROUND_HALF_UP"))

    # Sanity check: each item must fit in at least one core
    for wi in widths:
        if wi > L:
            raise ValueError("An item width is larger than master_length; impossible to cut.")

    # ========================================================================
    # STEP 3: PATTERN GENERATION
    # ========================================================================
    
    # Generate all feasible cutting patterns
    patterns = _generate_all_patterns(L_eff, widths_eff)

    # ========================================================================
    # STEP 4: INTEGER OPTIMIZATION (EXACT SOLUTION)
    # ========================================================================
    
    # Initialize OR-Tools CBC solver for integer programming
    solver = pywraplp.Solver.CreateSolver("CBC")
    if solver is None:
        raise RuntimeError("OR-Tools CBC solver not available. Try reinstalling ortools.")

    # Create decision variables: x[j] = number of times to use pattern j
    x = [solver.IntVar(0, solver.infinity(), f"x_{j}") for j in range(len(patterns))]

    # Add demand constraints: ensure all pieces are cut
    m = len(widths)
    for i in range(m):
        solver.Add(sum(patterns[j][i] * x[j] for j in range(len(patterns))) >= qty[i])

    # Objective: minimize total number of cores used
    solver.Minimize(sum(x))

    # Solve the optimization problem
    status = solver.Solve()
    if status != pywraplp.Solver.OPTIMAL:
        return {}

    cores = int(round(solver.Objective().Value()))

    # ========================================================================
    # STEP 5: BUILD CUTTING PLAN AND CALCULATE WASTE
    # ========================================================================
    
    cutting_plan = []
    total_used_length_int = cores * L
    total_consumed_int = 0  # Pieces + kerf consumed

    # Process each pattern used in the solution
    for j, pat in enumerate(patterns):
        count = int(round(x[j].solution_value()))
        if count <= 0:
            continue

        # Calculate actual material used per core with this pattern
        # Formula: used = sum(a_i * width_i) + (n-1) * kerf
        n_pieces = sum(pat)
        used_pieces_int = sum(pat[i] * widths[i] for i in range(m))
        used_kerf_int = max(0, n_pieces - 1) * k
        used_total_int = used_pieces_int + used_kerf_int

        # Verify pattern feasibility (should always pass)
        if used_total_int > L:
            raise RuntimeError("Generated an infeasible pattern under kerf model. Bug in generation.")

        total_consumed_int += used_total_int * count

        # Build pattern dictionary for output
        pattern_dict = {}
        for i, c in enumerate(pat):
            if c > 0:
                pattern_dict[float(widths_f[i])] = int(c)

        cutting_plan.append({
            "pattern": pattern_dict,
            "count": count,
        })

    # ========================================================================
    # STEP 6: COMPUTE WASTE METRICS
    # ========================================================================
    
    waste_int = total_used_length_int - total_consumed_int
    total_waste = float(Decimal(waste_int) / Decimal(scale))
    total_used = float(Decimal(total_used_length_int) / Decimal(scale))
    waste_percent = (total_waste / total_used * 100.0) if total_used > 0 else 0.0

    return {
        "cores_required": cores,
        "total_waste": total_waste,
        "total_waste_percent": waste_percent,
        "cutting_plan": cutting_plan,
    }