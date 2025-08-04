# Data Analysis Pro 🚀

A professional-grade data analysis and visualization application built with **PySide6** (Qt for Python). This application provides a modern, intuitive interface for comprehensive data analysis tasks.

## ✨ Features

### 📊 Data Import & Preview
- Load CSV and Excel files with intelligent file detection
- Interactive data preview with pagination
- Comprehensive metadata display (rows, columns, missing values, memory usage)
- Column type analysis and statistics
- Professional table interface with sorting and filtering

### 📈 Interactive Plotting 
- Multiple plot types: line, scatter, bar, boxplot, histogram
- Customizable axis labels and titles
- Grid and scientific notation options
- Export to PNG, PDF, and LaTeX (TikZ/PGFPlots)
- Embedded matplotlib integration with Qt

### 📋 Statistical Analysis
- Descriptive statistics (mean, median, std, min, max, variance)
- Hypothesis testing (t-test, ANOVA)
- Correlation analysis (Pearson/Spearman)
- Professional results display

### 🔬 Signal Processing
- Digital signal filtering (low-pass, high-pass, band-pass)
- FFT analysis and frequency domain visualization
- Signal comparison (original vs processed)
- Export capabilities for signal plots

## 🎨 Why PySide6 Instead of Tkinter?

**PySide6 provides a significantly more professional appearance:**

### ✅ PySide6 Advantages:
- **Native look and feel** on all platforms (Windows, macOS, Linux)
- **Modern styling** with built-in themes and customization
- **Professional widgets** specifically designed for data applications
- **Excellent matplotlib integration** for embedded plots
- **High DPI support** for modern displays
- **Responsive layouts** that adapt to different screen sizes
- **Built-in dark/light theme support**
- **Industry standard** - used by professional applications

### ❌ Tkinter Limitations:
- Outdated, 1990s-style appearance
- Limited styling and theming options
- Poor high-DPI support
- Basic widgets that look unprofessional
- Inconsistent appearance across platforms

## 🚀 Installation & Setup

### 1. Prerequisites
Ensure you have Python 3.8+ installed:
```powershell
python --version
```

### 2. Install Dependencies
```powershell
# Navigate to the project directory
cd "C:\Users\corre\DataAnaly"

# Install all required packages
pip install -r requirements.txt
```

### 3. Run the Application
```powershell
python main.py
```

## 📋 Dependencies

- **PySide6** >= 6.4.0 - Modern Qt-based GUI framework
- **qdarktheme** >= 2.1.0 - Professional dark/light themes
- **pandas** >= 2.0.0 - Data manipulation and analysis
- **matplotlib** >= 3.7.0 - Plotting and visualization
- **numpy** >= 1.24.0 - Numerical computing
- **scipy** >= 1.10.0 - Scientific computing and signal processing
- **seaborn** >= 0.12.0 - Statistical data visualization
- **openpyxl** >= 3.1.0 - Excel file support

## 🏗️ Project Structure

```
DataAnaly/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── README.md                       # Project documentation
└── src/                           # Source code
    ├── core/                      # Core functionality
    │   ├── __init__.py
    │   └── data_manager.py        # Centralized data management
    └── gui/                       # User interface
        ├── __init__.py
        ├── main_window.py         # Main application window
        └── tabs/                  # Individual tab modules
            ├── __init__.py
            ├── data_import_tab.py    # Data import interface
            ├── plotting_tab.py       # Plotting interface
            ├── statistics_tab.py     # Statistics interface
            └── signal_processing_tab.py # Signal processing interface
```

## 🎯 Professional Features

### Modern UI/UX
- **Dark/Light theme support** with automatic detection
- **Responsive layouts** that adapt to window resizing
- **Professional icons** and consistent styling
- **Status bar** with real-time feedback
- **Progress indicators** for long-running operations
- **Keyboard shortcuts** for power users

### Data Management
- **Centralized data manager** for efficient memory usage
- **Intelligent file detection** and loading
- **Error handling** with user-friendly messages
- **Export capabilities** in multiple formats

### Performance
- **Efficient data preview** (shows first 100 rows)
- **Memory usage monitoring**
- **Background processing** for large datasets
- **Optimized Qt widgets** for fast rendering

## 🚀 Getting Started

1. **Install and run** the application
2. **Load your data** using the "Load Data File" button
3. **Preview your dataset** in the interactive table
4. **Switch between tabs** to access different analysis tools
5. **Export results** in your preferred format

## 🛠️ Customization

The application is built with modularity in mind:
- Each tab is a separate module for easy extension
- Centralized data manager for consistent data access
- Professional theming system for customization
- Modular plotting functions for reusability

## 🔧 Development

To extend the application:
1. Add new tab modules in `src/gui/tabs/`
2. Implement data processing functions in `src/core/`
3. Update the main window to include new tabs
4. Follow the existing code patterns for consistency

---

**Data Analysis Pro** - Professional data analysis made simple. 📊✨

## Features

### 📊 Tab 1: Data Import & Preview
- Load CSV and Excel files
- Interactive data table preview
- Dataset metadata display (rows, columns, missing values)

### 📈 Tab 2: Plotting
- Interactive plot generation with customizable parameters
- Multiple plot types: line, scatter, bar, boxplot, histogram
- Custom axis labels and titles
- Grid and scientific formatting options
- Export to PNG, PDF, and LaTeX (TikZ/PGFPlots)

### 📉 Tab 3: Statistical Analysis
- Comprehensive summary statistics
- Statistical tests: t-test, ANOVA, correlation analysis
- Support for Pearson and Spearman correlations

### 🔊 Tab 4: Signal Processing
- Digital signal filtering (low-pass, high-pass, band-pass)
- FFT analysis and frequency domain visualization
- Original vs processed signal comparison
- Signal plot export capabilities

## Installation

1. Clone or download this project
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

## Project Structure

```
DataAnaly/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── src/
│   ├── gui/               # GUI components
│   │   ├── main_window.py # Main application window
│   │   ├── data_tab.py    # Data import and preview
│   │   ├── plot_tab.py    # Plotting interface
│   │   ├── stats_tab.py   # Statistical analysis
│   │   └── signal_tab.py  # Signal processing
│   ├── core/              # Core functionality
│   │   ├── data_manager.py # Data handling
│   │   ├── plotter.py     # Plotting utilities
│   │   ├── statistics.py  # Statistical functions
│   │   └── signal_processing.py # Signal processing
│   └── utils/             # Utility functions
│       ├── file_io.py     # File operations
│       └── validators.py  # Input validation
└── README.md
```

## Requirements

- Python 3.8+
- tkinter (usually included with Python)
- pandas
- matplotlib
- numpy
- scipy
- seaborn
- openpyxl
- xlrd

## License

This project is open source and available under the MIT License.
