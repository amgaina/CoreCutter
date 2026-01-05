"""
Form Component Module

Renders the cutting pattern input form for the stock cutter optimizer.
Handles master core configuration, blade size, cut piece inputs, and form submission.

Author: Abhishek Amgain
Company: Mid South Extrusion
Date: January 2026
"""

import streamlit as st
from .helper_num_core import optimize_unlimited_stock_gg


def form_component(quantity_master_core: bool = False):
	# Render form header with MSE branding
	st.markdown("""
		<div style='background:#fff;border-radius:10px;padding:28px 32px 24px 32px;box-shadow:0 4px 16px rgba(10,76,146,0.07);max-width:520px;margin:auto;'>
			<h3 style='color:#0a4c92;margin-bottom:18px;text-align:center;'>Cutting Pattern Input</h3>
		</div>
	""", unsafe_allow_html=True)

	# Create the input form container
	with st.form(key="cutting_form"):
		# Master core configuration - layout depends on mode
		if quantity_master_core:
			# Limited stock mode: ask for both length and quantity
			cols = st.columns(2)
			with cols[0]:
				master_core_length = st.number_input("Master Core Length (inches)", min_value=0.00, step=1.00, max_value= 1000.00, format="%.2f")
			with cols[1]:
				master_core_qty = st.number_input("Quantity of Master Cores", min_value=1, step=1, max_value = 1000,format="%d")
		else:
			# Unlimited stock mode: only ask for length
			master_core_length = st.number_input("Master Core Length (inches)", min_value=0.00, step=1.00, max_value= 1000.00, format="%.2f")
			master_core_qty = None

		# Blade size (kerf) input - affects total material loss in calculations
		blade_size = st.number_input(
			"Blade Size / Kerf (inches)", 
			min_value=0.00, 
			value=0.25, 
			step=0.05, 
			max_value=1.00, 
			format="%.2f",
			help="Width of the blade cut between pieces (default: 0.25 inches)"
		)

		st.markdown("<hr style='margin:18px 0 10px 0;border:0;border-top:1.5px solid #eee;'>", unsafe_allow_html=True)
		st.markdown("<b style='font-size:16px;'>Cut Piece Sizes</b>", unsafe_allow_html=True)

		# Initialize cut pieces in session state
		if "cut_pieces" not in st.session_state or not isinstance(st.session_state.cut_pieces, list):
			st.session_state.cut_pieces = [{"size": 1, "qty": 1}]

		# Render each cut piece row
		remove_index = None
		for i, piece in enumerate(st.session_state.cut_pieces):
			cols = st.columns([2, 2, 0.8])
			with cols[0]:
				size = st.number_input(f"Size #{i+1} (inches)", min_value=0.00, step=1.00, max_value=1000.00, format="%.2f", key=f"size_{i}")
			with cols[1]:
				qty = st.number_input(f"Qty #{i+1}", min_value=1, step=1, max_value=1000, format="%d", key=f"qty_{i}")
			with cols[2]:
				st.markdown("<div style='display:flex;align-items:flex-end;height:100%;justify-content:center;padding-bottom:8px;'>", unsafe_allow_html=True)
				if len(st.session_state.cut_pieces) > 1:
					if st.form_submit_button("Remove", key=f"remove_{i}"):
						remove_index = i
				st.markdown("</div>", unsafe_allow_html=True)
			st.session_state.cut_pieces[i]["size"] = size
			st.session_state.cut_pieces[i]["qty"] = qty

		# Remove cut piece if requested
		if remove_index is not None:
			st.session_state.cut_pieces.pop(remove_index)
			st.rerun()

		# Action buttons on the same line
		st.markdown("<br>", unsafe_allow_html=True)
		btn_cols = st.columns([1, 1])
		with btn_cols[0]:
			add_clicked = st.form_submit_button("Add Piece Size", use_container_width=True)
			if add_clicked:
				st.session_state.cut_pieces.append({"size": 1.00, "qty": 1})
				st.rerun()
		
		with btn_cols[1]:
			submitted = st.form_submit_button("Compute", type="primary", use_container_width=True)

		if submitted:
			# Validation: no cut piece size can be greater than master core length
			invalid = any(float(piece["size"]) > float(master_core_length) for piece in st.session_state.cut_pieces)
			if invalid:
				st.error("Cut piece size cannot be greater than the master core length.")
				return None, None, None
			# Validation: no duplicate cut piece sizes
			sizes = [round(float(piece["size"]), 4) for piece in st.session_state.cut_pieces]
			if len(sizes) != len(set(sizes)):
				st.error("Cut piece sizes must be unique.")
				return None, None, None
			demands = [
				{"width": float(piece["size"]), "quantity": float(piece["qty"])}
				for piece in st.session_state.cut_pieces if piece["size"] and piece["qty"]
			]
			if master_core_length and demands:
				result = optimize_unlimited_stock_gg(master_core_length, demands, kerf=blade_size)
				cores_required = result.get("cores_required", 0)
				if quantity_master_core:
					if master_core_qty < cores_required:
						st.error("You'll need more master core in the stock...... It won't be able to divided into those cut sizes...")
						return None, None, None
				
				# Store result and form inputs in session state
				st.session_state.optimization_result = {
					"result": result,
					"master_length": master_core_length,
					"kerf": blade_size
				}
				
				# Clear the form after successful computation
				st.session_state.cut_pieces = [{"size": 1, "qty": 1}]
				st.success("Optimization complete!")
			return master_core_length, master_core_qty, st.session_state.cut_pieces
	return None, None, None