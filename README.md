# CoreCut - Plastic Core Cutter

**Mid South Extrusion, Monroe, Louisiana**

A web-based optimization tool for solving the 1D cutting stock problem in plastic core manufacturing. CoreCut calculates the most efficient way to cut master cores into required piece sizes while minimizing material waste.

---

## 📋 Overview

CoreCut is a production planning tool for Mid South Extrusion's plastic core cutting operations. It uses the **Gilmore-Gomory column generation algorithm** to solve cutting stock optimization problems, providing optimal cutting patterns that minimize waste and master core usage.

### Key Features

- **Dual Operating Modes**:
  - **Mode 1**: Calculate minimum number of master cores needed for a given demand
  - **Mode 2**: Generate cutting patterns from existing inventory (limited stock)
- **Advanced Optimization Engine**:

  - Exact optimal solutions using OR-Tools CBC linear solver
  - Gilmore-Gomory column generation algorithm
  - Support for decimal precision (Python Decimal type)
  - Kerf (blade cut width) modeling for realistic cutting scenarios

- **Professional Interface**:

  - Clean, MSE-branded Streamlit web interface
  - Real-time calculation and visual pattern display
  - Downloadable cutting plans (.txt format)
  - Waste analysis and efficiency metrics

- **Production-Ready**:
  - Handles high-precision decimal measurements
  - Accounts for blade kerf (material loss between cuts)
  - Generates detailed per-core cutting instructions

---

## 🎯 How It Works

### Problem Statement

Given:

- Master cores of a fixed length (e.g., 120 inches)
- Demand for various piece sizes (e.g., 45", 36", 28")
- Blade kerf/width (e.g., 0.25 inches lost per cut)

Find:

- **Minimum number of master cores** needed to fulfill all demands
- **Optimal cutting patterns** that minimize waste

### Solution Approach

CoreCut implements the **Gilmore-Gomory column generation algorithm**:

1. **Pattern Generation**: Enumerates all feasible cutting patterns using depth-first search
2. **Integer Scaling**: Converts decimal measurements to integers for exact computation
3. **Linear Programming**: Solves the set covering problem using OR-Tools CBC solver
4. **Kerf Modeling**: Accounts for blade width loss: `(n-1) × kerf` for n pieces per core

**Mathematical Model**:

```
Minimize: Σ x_j (number of cores used with pattern j)
Subject to: Σ a_ij × x_j ≥ d_i (satisfy demand for each piece size i)
            x_j ≥ 0, integer

Where:
  - a_ij = number of pieces of size i in pattern j
  - d_i = demand for piece size i
  - Pattern feasibility: Σ(a_ij × w_i) + (Σa_ij - 1) × kerf ≤ master_length
```

---

## 🚀 Usage Guide

### Mode 1: Calculate Number of Master Cores (Unlimited Stock)

**Use Case**: You have unlimited master cores and need to determine how many are required.

**Steps**:

1. Click **"Calculate"** button
2. Enter **Master Core Length** (e.g., 120.00 inches)
3. Enter **Blade Size/Kerf** (e.g., 0.25 inches)
4. Add each **Cut Piece Size** and **Quantity**:
   - Size #1: 45.00" × 4 pieces
   - Size #2: 36.00" × 3 pieces
   - Size #3: 28.00" × 2 pieces
5. Click **"Compute"**

**Output**:

- Minimum cores required
- Detailed cutting pattern for each core
- Waste per core and total waste percentage
- Downloadable cutting plan

### Mode 2: Generate Cutting Patterns from Inventory (Limited Stock)

**Use Case**: You have a fixed number of master cores and need cutting patterns.

**Steps**:

1. Click **"Generate"** button
2. Enter **Master Core Length** and **Quantity Available**
3. Enter **Blade Size/Kerf**
4. Add **Cut Piece Sizes** and **Quantities Needed**
5. Click **"Compute"**

**Output**:

- Cutting patterns using available inventory
- Feasibility analysis (can demand be met?)
- Per-core cutting instructions
- Material utilization metrics

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the repository**

   ```bash
   cd /path/to/MSE_CoreCutter
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

**Development Mode:**

```bash
streamlit run app.py
```

**Using Launcher:**

```bash
python launcher.py
```

The application will automatically:

- Start the Streamlit server on port 8501
- Open your default web browser
- Navigate to http://localhost:8501

---

## 📁 Project Structure

```
MSE_CoreCutter/
├── app.py                  # Main Streamlit application entry point
├── launcher.py             # Auto-launching script with browser opener
├── requirements.txt        # Python dependencies
├── mse_logo.png           # Company logo (MSE branding)
├── CoreCut.spec           # PyInstaller specification file
├── pages/                 # Application modules
│   ├── __init__.py
│   ├── landing_page.py    # Header, mode selection, page navigation
│   ├── form_component.py  # Input form for cutting requirements
│   ├── display_result.py  # Results visualization and export
│   └── helper_num_core.py # Optimization engine (Gilmore-Gomory algorithm)
├── venv/                  # Python virtual environment
└── README.md              # This file
```

### Installing Dependencies

1. **Activate virtual environment**:

   ```bash
   source venv/bin/activate
   ```

2. **Install packages from requirements.txt**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🛠️ Technologies Used

- **Streamlit**: Web application framework
- **OR-Tools**: Google's optimization library for cutting optimization
- **Pillow (PIL)**: Image processing for logo display
- **PyInstaller**: Packaging tool for creating standalone executables

---

## 📦 Building for Distribution

To create a portable executable that can be distributed to end users without requiring Python installation, PyInstaller will be used.

**Coming Soon**: Build instructions and scripts will be added for packaging the application as a standalone executable.

### For End Users (Future)

Once the application is built and packaged:

1. Extract the ZIP file to desired location
2. Open the CoreCut folder
3. Double-click the `CoreCut` application
4. Application will automatically launch in your default web browser

---

## 🔧 Development

### Architecture

**Module Responsibilities**:

- **`app.py`**:

  - Main entry point with Streamlit configuration
  - Global styling and MSE branding
  - Page setup and resource path handling for PyInstaller

- **`launcher.py`**:

  - Auto-launch script with browser integration
  - Automatically opens http://localhost:8501 on startup
  - Daemon thread for non-blocking browser launch

- **`pages/landing_page.py`**:

  - Renders MSE header with logo
  - Two-column mode selection cards
  - Page navigation state management
  - Footer with company information

- **`pages/form_component.py`**:

  - Dynamic input form for cutting parameters
  - Master core configuration (length, optional quantity)
  - Blade kerf input with validation
  - Dynamic cut piece management (add/remove)
  - Input validation (duplicates, size constraints)

- **`pages/helper_num_core.py`**:

  - **Core optimization engine**
  - Gilmore-Gomory column generation implementation
  - Decimal-safe integer scaling
  - Pattern enumeration via DFS
  - OR-Tools CBC solver integration
  - Kerf modeling: `sum(a_i × (w_i + kerf)) ≤ master_length + kerf`

- **`pages/display_result.py`**:
  - Visual result rendering with colored bars
  - Per-core cutting pattern display
  - Waste analysis and efficiency metrics
  - Text export generation for cutting plans
  - Download button for production use

### Algorithm: Gilmore-Gomory Column Generation

**Phase 1: Pattern Enumeration**

```python
def _generate_all_patterns(L, widths):
    # DFS to enumerate all feasible patterns
    # Pattern feasibility: sum(pattern[i] × widths[i]) ≤ L
    # Returns: List of all valid cutting patterns
```

**Phase 2: Integer Scaling**

```python
def _decimal_scale_factor(values):
    # Convert decimals to integers for exact computation
    # Scale = 10^k where k = max decimal places
    # Prevents floating-point precision issues
```

**Phase 3: Linear Programming**

```python
solver = pywraplp.Solver.CreateSolver('CBC')
# Minimize: sum of pattern usage counts
# Subject to: demand satisfaction constraints
# Returns: Optimal integer solution
```

### Kerf Handling

The application models realistic cutting scenarios where blade width causes material loss:

- **Kerf Loss Formula**: For a pattern with `n` pieces, kerf loss = `(n - 1) × kerf`
- **Transformed Constraint**: `sum(a_i × (w_i + kerf)) ≤ master_length + kerf`
- **This ensures** patterns account for the blade cuts between pieces

### Data Flow

```
User Input → Form Validation → Decimal Conversion → Pattern Generation
    ↓
Integer Scaling → OR-Tools Solver → Optimal Solution
    ↓
Result Processing → Visual Display → Exportable Plan
```

### Styling

The application uses custom CSS for Mid South Extrusion branding:

- Primary color: `#0a4c92` (MSE Blue)
- Clean white background
- Professional typography and spacing

---

## 📝 Requirements

```
streamlit
pillow
ortools
pyinstaller
```

---

## 👨‍💻 Author

**Abhishek Amgain**  
Mid South Extrusion  
January 2026

---

## 📄 License

Proprietary - Mid South Extrusion

---

## 🐛 Troubleshooting

### Application won't start

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.12+)

### Port already in use

- Another application is using port 8501
- Stop other Streamlit apps or change the port in `launcher.py`

### Build issues (PyInstaller)

- Ensure PyInstaller is installed: `pip install pyinstaller`
- Clear previous builds: `rm -rf build dist`
- Run build script from project root directory

---

## 🔮 Future Enhancements

- [ ] Save cutting patterns to PDF
- [ ] Historical cutting data analysis
- [ ] Multi-material support
- [ ] Advanced reporting features
- [ ] User preferences and settings

---

## 📞 Support

For technical support or questions, contact:  
**Mid South Extrusion**  
Developer: Abhishek Amgain
# CoreCutter
