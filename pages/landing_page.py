"""
Landing Page Module

Main page for the MSE Stock Cutter application.
Displays welcome header, mode selection cards, and routes to optimization workflows.

Author: Abhishek Amgain
Company: Mid South Extrusion
Date: January 2026
"""

import streamlit as st
from PIL import Image
import os
from .form_component import form_component
from .display_result import display_result


def render_header():
	"""Render the application header with MSE branding and logo."""
	logo_col, text_col = st.columns([1, 9])
	
	with logo_col:
		# Try to load company logo, fallback to SVG shield if not found
		logo_path = "./mse_logo.png"
		if os.path.exists(logo_path):
			img = Image.open(logo_path)
			st.image(img, width=80)
		else:
			st.markdown(
				"""
				<div style='width:80px;height:80px;border-radius:12px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#0a4c92,#F7A800);box-shadow:0 6px 16px rgba(10,76,146,0.12);'>
					<svg width='40' height='40' viewBox='0 0 24 24' fill='white'><path d='M12 2L2 7v10c0 5.55 3.84 9.74 9 11 5.16-1.26 9-5.45 9-11V7l-10-5z'/></svg>
				</div>
				""",
				unsafe_allow_html=True,
			)
	
	with text_col:
		st.markdown(
			"""
			<div style='display:flex;align-items:center;height:80px;'>
				<div>
					<h1 style='margin:0;padding:0;font-weight:800;font-size:32px;line-height:1.2;color:#0a4c92;'>Mid South Extrusion</h1>
					<div style='margin-top:4px;font-size:16px;color:#333;font-weight:600;'>Plastic Core Cutter</div>
					<div style='margin-top:2px;font-size:13px;color:#666;'>Monroe, Louisiana</div>
				</div>
			</div>
			""",
			unsafe_allow_html=True
		)


def render_landing_page():
	"""Render the main landing page with mode selection and form display."""
	
	st.markdown("---")

	# Initialize session state for page navigation
	if 'page' not in st.session_state:
		st.session_state['page'] = 'home'

	# Initialize session state for form mode selection
	if 'show_form' not in st.session_state:
		st.session_state['show_form'] = None

	if st.session_state['page'] == 'home':
		# Display two-column layout with mode selection cards
		col1, col2 = st.columns(2, gap='large')
		
		# Left column: Unlimited stock mode
		with col1:
			st.markdown(
				"""
				<div class='mse-card' style='background:white;margin-bottom:10px;border-radius:10px;border-left:6px solid var(--primary);box-shadow:0 6px 18px rgba(10,76,146,0.06)'>
					<div style='padding:18px;'>
						<h3 style='margin:0 0 8px 0;color:var(--primary)'>1) Calculate Number of Master Cores</h3>
						<ul>
							<li>Provide piece sizes and quantities.</li>
							<li>Computes the minimum number of master cores and cutting patterns.</li>
							<li>Shows waste per core.</li>
						</ul>
					</div>
				</div>
				""",
				unsafe_allow_html=True,
			)
			if st.button('Calculate', key='home_unlimited'):
				st.session_state['show_form'] = 'unlimited'

		# Right column: Limited stock mode
		with col2:
			st.markdown(
				"""
				<div class='mse-card' style='background:white;margin-bottom:10px;border-radius:10px;border-left:6px solid var(--primary);box-shadow:0 6px 18px rgba(10,76,146,0.06)'>
					<div style='padding:18px;'>
						<h3 style='margin:0 0 8px 0;color:var(--primary)'>2) Generate Cutting Patterns From Inventory</h3>
						<ul>
							<li>Provide master core lengths and counts</li>
							<li>Provide piece sizes and quantities.</li>
							<li>Compute cutting patterns to meet demand and show waste per core.</li>
						</ul>
					</div>
				</div>
				""",
				unsafe_allow_html=True,
			)
			if st.button('Generate', key='home_limited'):
				st.session_state['show_form'] = 'limited'

		# Render the appropriate form based on user selection
		if st.session_state['show_form'] == 'unlimited':
			form_component(quantity_master_core=False)  # Unlimited stock mode

		elif st.session_state['show_form'] == 'limited':
			form_component(quantity_master_core=True)  # Limited stock mode

		# Display optimization results (rendered outside form to avoid API errors)
		if "optimization_result" in st.session_state:
			opt_data = st.session_state.optimization_result
			result = opt_data["result"]
			display_result(
				cores_required=result.get("cores_required", 0),
				total_waste=result.get("total_waste", 0.0),
				total_waste_percent=result.get("total_waste_percent", 0.0),
				cutting_plan=result.get("cutting_plan", []),
				master_length=opt_data["master_length"],
				kerf=opt_data["kerf"]
			)

	# Footer section with company info
	st.markdown("---")
	st.markdown("<div style='text-align:center;color:#666;padding:8px 0'>© 2025 Mid South Extrusion - Monroe, LA</div>", unsafe_allow_html=True)


if __name__ == "__main__":
	render_header()
	render_landing_page()
