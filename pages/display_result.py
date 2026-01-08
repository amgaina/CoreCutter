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

def _generate_plan_text(cores_required, total_waste, total_waste_percent, cutting_plan, master_length, kerf):
	"""
	Generate a formatted text representation of the cutting plan.
	Used for exporting optimization results as a downloadable .txt file.
	
	Args:
		cores_required (int): Number of master cores needed
		total_waste (float): Total waste material across all cores
		total_waste_percent (float): Waste as percentage of total material
		cutting_plan (list): List of patterns with piece counts and usage
		master_length (float): Master core length in inches
		kerf (float): Blade cut width in inches
		
	Returns:
		str: Multi-line text formatted cutting plan with header, summary, and per-core details
	"""
	lines = []
	
	# Header section with timestamp
	lines.append("=" * 70)
	lines.append("MSE STOCK CUTTER - CUTTING PLAN")
	lines.append("=" * 70)
	lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
	lines.append("")
	
	# Summary section with key metrics
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
			# Kerf logic: 0 if pieces exactly equal core length, otherwise at least one kerf
			kerf_loss = 0.0 if abs(pieces_length - master_length) < 1e-6 else float(kerf)
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

def display_result(cores_required, total_waste, total_waste_percent, cutting_plan, master_length=None, kerf=0.25):
	"""
	Display cutting stock optimization results in a user-friendly format.
	
	Renders a visual summary with:
	- Total cores required and waste metrics
	- Detailed cutting patterns with visual bars
	- Per-pattern breakdown showing pieces, kerf loss, and waste
	
	Args:
		cores_required (int): Number of master cores needed
		total_waste (float): Total waste material across all cores
		total_waste_percent (float): Waste as percentage of total material
		cutting_plan (list): List of patterns with piece counts and usage
		master_length (float, optional): Master core length for display calculations
		kerf (float, optional): Blade cut width (default: 0.25 inches)
	"""
	
	# Use provided master_length or default to safe fallback
	if master_length is None or master_length <= 0:
		master_length = 100.0

	# -------------------------------------------------------------------------
	# Responsive CSS for smaller screens
	# -------------------------------------------------------------------------
	st.markdown(
		"""
		<style>
		/* Base classes */
		.mse-summary h2 { margin-bottom: 12px; text-align: center; }
		.mse-core-bar { display: flex; border-radius: 6px; overflow: hidden; height: 35px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
		.mse-segment { color: #fff; font-size: 10px; line-height: 35px; text-align: center; overflow: hidden; }
		.mse-piece-chip { display:inline-block; background:#0a4c92; color:white; padding:3px 8px; border-radius:4px; margin:0 3px 0 0; font-size:11px; }
		.mse-legend { background:#f8f9fa; border-radius:8px; padding:14px; margin:12px 0 18px 0; }

		/* Force Streamlit metric colors to black */
		[data-testid="stMetricValue"] { color: #000 !important; }
		[data-testid="stMetricLabel"] { color: #000 !important; }
		[data-testid="stMetricDelta"] { color: #000 !important; }

		/* Tablet */
		@media (max-width: 768px) {
		  .mse-summary h2 { font-size: 18px !important; }
		  .mse-core-bar { height: 28px !important; }
		  .mse-segment { font-size: 9px !important; line-height: 28px !important; }
		  .mse-piece-chip { font-size:10px !important; padding:2px 6px !important; }
		}

		/* Mobile */
		@media (max-width: 480px) {
		  .mse-core-bar { height: 22px !important; }
		  .mse-segment { font-size: 8px !important; line-height: 22px !important; }
		  .mse-piece-chip { display:none; }
		}
		</style>
		""",
		unsafe_allow_html=True
	)
	
	# Render summary card with key optimization metrics
	st.markdown(f"""
		<div class='mse-summary' style='background:#f7fafc;border-radius:12px;padding:20px 24px 16px 24px;
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
	# Summary Statistics Section (moved to top)
	# -------------------------------------------------------------------------
	st.markdown(
		"<h3 style='text-align:center;color:#000000;margin:16px 0 12px 0;font-size:16px;'> Overall Statistics</h3>", 
		unsafe_allow_html=True
	)
	
	# Summary metrics
	total_master_length = cores_required * master_length
    
	col1, col2, col3, col4 = st.columns(4)
	with col1:
		st.metric("Total Cores", cores_required, delta=None, delta_color="off")
	with col2:
		st.metric("Total Material", f"{total_master_length:.2f}\"", delta=None, delta_color="off")
	with col3:
		st.metric("Material Used", f"{(total_master_length - total_waste):.2f}\"", delta=None, delta_color="off")
	with col4:
		st.metric("Total Waste", f"{total_waste:.2f}\"")

	# -------------------------------------------------------------------------
	# Color Legend (moved to top, just after overall statistics)
	# -------------------------------------------------------------------------
	st.markdown(
		"""
		<div class='mse-legend'>
			<div style='font-weight:600;margin-bottom:10px;color:#0a4c92;font-size:13px;'>Color Legend:</div>
			<div style='display:flex;gap:20px;flex-wrap:wrap;font-size:12px;'>
				<div style='display:flex;align-items:center;gap:6px;'>
					<div style='width:20px;height:20px;background:#0a4c92;border-radius:3px;'></div>
					<span><b>Blue</b> = Cut Pieces</span>
				</div>
				<div style='display:flex;align-items:center;gap:6px;'>
					<div style='width:20px;height:20px;background:#8B6F47;border-radius:3px;'></div>
					<span><b>Brown</b> = Waste</span>
				</div>
			</div>
		</div>
		""",
		unsafe_allow_html=True
	)
	
	# -------------------------------------------------------------------------
	# Render Cutting Plan Patterns with Visual Bars
	# -------------------------------------------------------------------------
	st.markdown(
		"<h3 style='text-align:center;color:#0a4c92;margin:20px 0 16px 0;font-size:18px;'> Cutting Plan by Core</h3>", 
		unsafe_allow_html=True
	)
	
	# Build all cores data
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
			# Kerf logic: 0 if pieces exactly equal core length, otherwise at least one kerf
			kerf_loss = 0.0 if abs(pieces_length - master_length) < 1e-6 else float(kerf)
			used_length = pieces_length + kerf_loss
			waste = master_length - used_length
			waste_percent = (waste / master_length * 100.0) if master_length > 0 else 0.0
			
			# Build visual bar with pieces (blue) + waste (brown)
			bar_segments = []
			
			# Add segments for each cut piece size (BLUE)
			for width, qty in sorted(pattern.items()):
				seg_length = float(width) * int(qty)
				width_pct = 100 * seg_length / master_length
				bar_segments.append({
					"type": "piece",
					"width_pct": width_pct,
					"label": f"{qty}×{width:.2f}\"",
					"value": seg_length
				})
			
			# Add waste segment (BROWN)
			if waste > 0:
				waste_pct = 100 * waste / master_length
				bar_segments.append({
					"type": "waste",
					"label":"",
					"width_pct": waste_pct,
					"value": waste
				})
			
			# Store core data for rendering
			cores_data.append({
				"number": core_number,
				"segments": bar_segments,
				"waste": waste,
				"waste_percent": waste_percent,
				"pieces_length": pieces_length,
				"kerf_loss": kerf_loss,
				"used_length": used_length,
				"pattern": pattern
			})
	
	# Render each core with detailed information (flip order: bottom-to-top)
	for core_info in reversed(cores_data):
		# Core info row with number and waste
		col_num, col_bar, col_waste = st.columns([0.8, 8, 1.5])
		
		with col_num:
			st.markdown(f"<div style='font-weight:bold;font-size:13px;'>Core {core_info['number']}</div>", unsafe_allow_html=True)
		
		with col_bar:
			# Visual cutting bar
			bar_html = "<div class='mse-core-bar'>"
			
			for segment in core_info["segments"]:
				if segment["type"] == "piece":
					color = "#0a4c92"  # Blue for cut pieces
				else:  # waste
					color = "#8B6F47"  # Brown for waste
				
				title = segment["label"]
				bar_html += (
					f"<div class='mse-segment' style='display:inline-block;width:{segment['width_pct']:.2f}%;height:100%;background:{color};'"
					f" title='{title}: {segment['value']:.2f}\"'>"
					f"<span style='font-weight:600;'>{title}</span>"
					f"</div>"
				)
			
			bar_html += "</div>"
			st.markdown(bar_html, unsafe_allow_html=True)
		
		with col_waste:
			st.markdown(
				f"<div style='font-size:12px;text-align:right;font-weight:600;'>"
				f"<div style='color:#d9534f;'>{core_info['waste']:.2f}\"</div>"
				f"<div style='font-size:11px;color:#666;'>{core_info['waste_percent']:.1f}%</div>"
				f"</div>",
				unsafe_allow_html=True
			)
		
		# Compact metrics and details in one line
		col_metrics, col_kerf = st.columns([3, 1.5])
		
		with col_metrics:
			pieces_info = []
			for width in sorted(core_info["pattern"].keys()):
				qty = core_info["pattern"][width]
				pieces_info.append(f"<span class='mse-piece-chip'><b>{qty}×</b>{width:.2f}\"</span>")
			
			st.markdown(" ".join(pieces_info), unsafe_allow_html=True)
		
		with col_kerf:
			st.markdown(
				f"<div style='font-size:11px;text-align:right;color:#666;'>"
				f"<div>Kerf: <b style='color:#dc3545;'>{core_info['kerf_loss']:.2f}\"</b></div>"
				f"<div style='color:#666;'>Waste: <b>{core_info['waste']:.2f}\"</b></div>"
				f"</div>",
				unsafe_allow_html=True
			)
		
		# Minimal divider
		st.markdown("<div style='margin:8px 0;border-top:1px solid #e8e8e8;'></div>", unsafe_allow_html=True)
	
	# Legend already shown at the top
	
	# -------------------------------------------------------------------------
	# Export Section
	# -------------------------------------------------------------------------
	st.markdown("<br><br>", unsafe_allow_html=True)
	st.markdown(
		"<h3 style='text-align:center;color:#0a4c92;margin-bottom:16px;'>Export Cutting Plan</h3>", 
		unsafe_allow_html=True
	)
	
	col_export = st.columns([1, 3])
	with col_export[0]:
		# Generate text plan with correct parameters
		plan_text = _generate_plan_text(cores_required, total_waste, total_waste_percent, cutting_plan, master_length, kerf)
		st.download_button(
			label="Export as TXT",
			data=plan_text,
			file_name=f"cutting_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
			mime="text/plain",
			use_container_width=True
		)
