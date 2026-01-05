"""
Result Display Module

Renders optimization results with visual cutting patterns and waste analysis.
Displays master core usage, cutting plans, and material efficiency metrics.

Author: Abhishek Amgain
Company: Mid South Extrusion
Date: January 2026
"""

import streamlit as st
from datetime import datetime


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _generate_plan_text(result, master_length, kerf):
	"""
	Generate a formatted text representation of the cutting plan.
	Used for exporting optimization results as a downloadable .txt file.
	
	Args:
		result (dict): Optimization result from the solver
		master_length (float): Master core length in inches
		kerf (float): Blade cut width in inches
		
	Returns:
		str: Multi-line text formatted cutting plan with header, summary, and per-core details
	"""
	cutting_plan = result.get("cutting_plan", [])
	lines = []
	
	# Header section with timestamp
	lines.append("=" * 70)
	lines.append("MSE STOCK CUTTER - CUTTING PLAN")
	lines.append("=" * 70)
	lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
	lines.append("")
	
	# Summary section with key metrics
	cores_required = result.get("cores_required", 0)
	total_waste = result.get("total_waste", 0)
	total_waste_percent = result.get("total_waste_percent", 0)
	
	lines.append("SUMMARY")
	lines.append("-" * 70)
	lines.append(f"Cores Required:              {cores_required}")
	lines.append(f"Master Core Length (inches): {master_length:.2f}\"")
	lines.append(f"Blade Size / Kerf (inches):  {kerf:.2f}\"")
	lines.append(f"Total Waste (inches):        {total_waste:.2f}\"")
	lines.append(f"Total Waste %:               {total_waste_percent:.2f}%")
	lines.append("")
	
	# Detailed cutting plan by core
	lines.append("CUTTING PLAN BY CORE")
	lines.append("-" * 70)
	
	core_num = 1
	for pattern_info in cutting_plan:
		pattern = pattern_info["pattern"]
		count = pattern_info["count"]
		
		# Repeat pattern for each usage count
		for rep in range(count):
			total_pieces = sum(int(qty) for qty in pattern.values())
			pieces_length = sum(float(width) * int(qty) for width, qty in pattern.items())
			kerf_loss = max(0, total_pieces - 1) * kerf
			waste = master_length - (pieces_length + kerf_loss)
			
			# Core header with piece and waste summary
			lines.append(f"\nCore {core_num}:")
			lines.append(f"  Pieces: {pieces_length:.2f}\" | Waste: {max(0, waste):.2f}\" ({max(0, waste/master_length*100):.1f}%)")
			
			# List all pieces in this core
			for width, qty in sorted(pattern.items()):
				lines.append(f"    - {int(qty)} × {width:.2f}\"")
			
			core_num += 1
	
	lines.append("")
	lines.append("=" * 70)
	lines.append("© 2026 Mid South Extrusion - Monroe, Louisiana")
	lines.append("=" * 70)
	
	return "\n".join(lines)

# =============================================================================
# RESULT DISPLAY FUNCTION
# =============================================================================

def display_result(result, master_length=None, kerf=0.25):
	"""
	Display cutting stock optimization results in a user-friendly format.
	
	Renders a visual summary with:
	- Total cores required and waste metrics
	- Detailed cutting patterns with visual bars
	- Per-pattern breakdown showing pieces, kerf loss, and waste
	
	Args:
		result (dict): Optimization result from optimize_unlimited_stock_gg containing:
			- cores_required (int): Number of master cores needed
			- total_waste (float): Total waste material across all cores
			- total_waste_percent (float): Waste as percentage of total material
			- cutting_plan (list): List of patterns with piece counts and usage
		master_length (float, optional): Master core length for display calculations
		kerf (float, optional): Blade cut width (default: 0.25 inches)
	"""
	
	# Extract key metrics from optimization result
	cores_required = result.get("cores_required", 0)
	total_waste = result.get("total_waste", 0.0)
	total_waste_percent = result.get("total_waste_percent", 0.0)
	cutting_plan = result.get("cutting_plan", [])
	
	# Use provided master_length or default to safe fallback
	if master_length is None or master_length <= 0:
		master_length = 100.0
	
	# Render summary card with key optimization metrics
	st.markdown(f"""
		<div style='background:#f7fafc;border-radius:12px;padding:20px 24px 16px 24px;
		            box-shadow:0 4px 16px rgba(10,76,146,0.10);max-width:650px;
		            margin:auto;margin-bottom:20px;'>
			<h2 style='color:#0a4c92;margin-bottom:12px;text-align:center;'>
				Optimization Results
			</h2>
			<div style='font-size:17px;font-weight:700;margin-bottom:6px;'>
				Cores Required: <span style='color:#F7A800'>{cores_required}</span>
			</div>
			<div style='font-size:15px;margin-bottom:4px;'>
				Master Core Length: <b>{master_length:.2f}"</b>
			</div>
			<div style='font-size:15px;margin-bottom:4px;'>
				Blade Size (Kerf): <b>{kerf:.2f}"</b>
			</div>
			<div style='font-size:15px;margin-bottom:4px;'>
				Total Waste: <b style='color:#d9534f'>{total_waste:.2f}"</b>
			</div>
			<div style='font-size:15px;'>
				Total Waste %: <b style='color:#d9534f'>{total_waste_percent:.2f}%</b>
			</div>
		</div>
	""", unsafe_allow_html=True)
	
	# -------------------------------------------------------------------------
	# Render Cutting Plan Patterns
	# -------------------------------------------------------------------------
	st.markdown(
		"<h4 style='margin-top:0;margin-bottom:16px;text-align:center;'>Cutting Plan by Core</h4>", 
		unsafe_allow_html=True
	)
	
	# Create a single horizontal view of all cores
	all_cores_html = ""
	
	# Build all cores data first (to reverse order)
	cores_data = []
	
	for idx, pattern_info in enumerate(cutting_plan, 1):
		pattern = pattern_info["pattern"]  # Dict of {width: quantity}
		count = pattern_info["count"]      # Times this pattern is used
		
		# Repeat this pattern 'count' times
		for rep in range(count):
			core_number = sum(cutting_plan[j]["count"] for j in range(idx - 1)) + rep + 1
			
			# Calculate metrics for this core
			total_pieces = sum(int(qty) for qty in pattern.values())
			pieces_length = sum(float(width) * int(qty) for width, qty in pattern.items())
			kerf_loss = max(0, total_pieces - 1) * kerf
			used_length = pieces_length + kerf_loss
			waste = master_length - used_length
			waste_percent = (waste / master_length * 100.0) if master_length > 0 else 0.0
			
			# Build bar for this core (pieces + waste only)
			bar_html = ""
			
			# Add segment for each cut piece size
			# Add segment for each cut piece size
			for width, qty in sorted(pattern.items()):
				seg_length = float(width) * int(qty)
				width_pct = 100 * seg_length / master_length
				
				bar_html += (
					f"<div style='display:inline-block;height:28px;width:{width_pct:.2f}%;"
					f"background:#0a4c92;color:#fff;text-align:center;font-size:11px;"
					f"line-height:28px;border-right:1px solid #fff;' "
					f"title='{qty} × {width}\"'>{qty}×{width}\"</div>"
				)
			
			# Store core data for rendering (will reverse order below)
			cores_data.append({
				"number": core_number,
				"bar_html": bar_html,
				"waste": waste,
				"waste_percent": waste_percent,
				"pieces_length": pieces_length,
				"kerf_loss": kerf_loss,
				"used_length": used_length
			})
	
	# Reverse the order (bottom to top)
	cores_data.reverse()
	
	# Render each core individually using Streamlit
	for core_info in cores_data:
		col1, col2 = st.columns([1, 8])
		with col1:
			st.markdown(f"**Core {core_info['number']}**")
		with col2:
			st.markdown(
				f"<div style='display:flex;border-radius:4px;overflow:hidden;'>"
				f"{core_info['bar_html']}"
				f"</div>",
				unsafe_allow_html=True
			)
	
	# -------------------------------------------------------------------------
	# Export Section
	# -------------------------------------------------------------------------
	st.markdown("<br>", unsafe_allow_html=True)
	
	col_export = st.columns([1, 3])
	with col_export[0]:
		# Generate text plan
		plan_text = _generate_plan_text(result, master_length, kerf)
		st.download_button(
			label="Export Plan",
			data=plan_text,
			file_name=f"cutting_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
			mime="text/plain",
			use_container_width=True
		)
