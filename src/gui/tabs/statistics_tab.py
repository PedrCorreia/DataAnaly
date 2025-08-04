"""
Advanced Statistics Tab for Data Analysis Application.

This module provides comprehensive statistical analysis and data transformation 
capabilities with full interoperability.
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures, StandardScaler, MinMaxScaler
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Import new modular statistics classes
from ...core.statistics import (
    DescriptiveStatistics, 
    RegressionAnalysis, 
    DataTransformations,
    CorrelationAnalysis,
    HypothesisTests
)

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel,
    QComboBox, QPushButton, QSpinBox, QDoubleSpinBox, QCheckBox, QLineEdit,
    QTextEdit, QScrollArea, QSplitter, QTabWidget, QTableWidget, 
    QTableWidgetItem, QFileDialog, QMessageBox, QProgressBar, QSlider,
    QListWidget, QListWidgetItem, QTreeWidget, QTreeWidgetItem
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont


class StatisticsTab(QWidget):
    """Advanced statistics interface with data generation capabilities and transformation tools."""
    
    # Signal to notify when new data is created
    data_created = Signal(str, pd.DataFrame)  # (name, dataframe)
    
    def __init__(self, data_manager):
        """Initialize the statistics tab."""
        super().__init__()
        self.data_manager = data_manager
        self.generated_datasets = {}  # Store generated statistical data
        self.analysis_results = {}    # Store analysis results and metadata
        self.regression_history = {}  # Store multiple regression analyses
        self.transformation_history = {}  # Store multiple transformation analyses
        
        # Initialize modular statistics classes
        self.descriptive_stats = DescriptiveStatistics()
        self.regression_analysis = RegressionAnalysis()
        self.data_transformations = DataTransformations()
        self.correlation_analysis = CorrelationAnalysis()
        self.hypothesis_tests = HypothesisTests()
        
        # Statistical analysis configuration
        self.stats_config = {
            'descriptive': {
                'basic': ['count', 'mean', 'std', 'min', 'max', 'median'],
                'advanced': ['variance', 'skewness', 'kurtosis', 'mode', 'range', 'iqr'],
                'percentiles': [5, 10, 25, 50, 75, 90, 95, 99],
                'confidence_intervals': [90, 95, 99]
            },
            'regression': {
                'types': ['linear', 'polynomial', 'ridge', 'lasso', 'exponential', 'logarithmic'],
                'polynomial_degrees': range(1, 11),
                'regularization_alphas': [0.01, 0.1, 1.0, 10.0, 100.0]
            },
            'transformations': {
                'mathematical': ['log', 'sqrt', 'power', 'reciprocal', 'standardize', 'normalize'],
                'statistical': ['zscore', 'robust_scale', 'quantile_transform', 'box_cox']
            }
        }
        
        self.setup_ui()
        self.setEnabled(False)  # Disabled until data is loaded
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        
        # Create main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Controls and configuration
        controls_widget = self.create_controls_panel()
        controls_widget.setMaximumWidth(450)
        controls_widget.setMinimumWidth(400)
        
        # Right panel - Results and visualization
        results_widget = self.create_results_panel()
        
        splitter.addWidget(controls_widget)
        splitter.addWidget(results_widget)
        splitter.setSizes([400, 1000])  # 30% controls, 70% results
        
        layout.addWidget(splitter)
        
    def create_controls_panel(self):
        """Create the left control panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area for controls
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Data Selection and Relationships Group
        data_group = self.create_data_selection_group()
        scroll_layout.addWidget(data_group)
        
        # Statistics Configuration Group
        stats_group = self.create_statistics_group()
        scroll_layout.addWidget(stats_group)
        
        # Regression Analysis Group
        regression_group = self.create_regression_group()
        scroll_layout.addWidget(regression_group)
        
        # Data Transformation Group
        transform_group = self.create_transformation_group()
        scroll_layout.addWidget(transform_group)
        
        # Export and Save Group
        export_group = self.create_export_group()
        scroll_layout.addWidget(export_group)
        
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        layout.addWidget(scroll)
        
        return widget
        
    def create_data_selection_group(self):
        """Create data selection and relationship analysis controls."""
        group = QGroupBox("📊 Data Selection & Relationships")
        layout = QGridLayout(group)
        
        # Primary dataset selection
        layout.addWidget(QLabel("Primary Dataset:"), 0, 0)
        self.primary_data_combo = QComboBox()
        self.primary_data_combo.currentTextChanged.connect(self.on_primary_data_changed)
        layout.addWidget(self.primary_data_combo, 0, 1)
        
        # Column selection for analysis
        layout.addWidget(QLabel("Analysis Columns:"), 1, 0)
        self.columns_list = QListWidget()
        self.columns_list.setMaximumHeight(120)
        self.columns_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(self.columns_list, 1, 1, 2, 1)
        
        # Related datasets (shows datasets with matching columns)
        layout.addWidget(QLabel("Related Datasets:"), 3, 0)
        self.related_data_tree = QTreeWidget()
        self.related_data_tree.setMaximumHeight(150)
        self.related_data_tree.setHeaderLabels(["Dataset", "Matching Columns", "Compatibility"])
        layout.addWidget(self.related_data_tree, 3, 1, 2, 1)
        
        # Refresh relationships button
        self.refresh_btn = QPushButton("🔄 Refresh Relationships")
        self.refresh_btn.clicked.connect(self.analyze_data_relationships)
        layout.addWidget(self.refresh_btn, 5, 0, 1, 2)
        
        return group
        
    def create_statistics_group(self):
        """Create statistical analysis controls."""
        group = QGroupBox("📈 Statistical Analysis")
        layout = QGridLayout(group)
        
        # Descriptive statistics options
        layout.addWidget(QLabel("Analysis Type:"), 0, 0)
        self.stats_type_combo = QComboBox()
        self.stats_type_combo.addItems([
            "Descriptive Statistics",
            "Correlation Analysis", 
            "Distribution Analysis",
            "Hypothesis Testing",
            "Time Series Analysis"
        ])
        self.stats_type_combo.currentTextChanged.connect(self.on_stats_type_changed)
        layout.addWidget(self.stats_type_combo, 0, 1)
        
        # Statistical measures selection
        layout.addWidget(QLabel("Measures:"), 1, 0)
        self.measures_list = QListWidget()
        self.measures_list.setMaximumHeight(100)
        self.measures_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.populate_measures_list()
        layout.addWidget(self.measures_list, 1, 1, 2, 1)
        
        # Confidence level
        layout.addWidget(QLabel("Confidence Level:"), 3, 0)
        self.confidence_spin = QSpinBox()
        self.confidence_spin.setRange(80, 99)
        self.confidence_spin.setValue(95)
        self.confidence_spin.setSuffix("%")
        layout.addWidget(self.confidence_spin, 3, 1)
        
        # Group by column (optional)
        layout.addWidget(QLabel("Group By:"), 4, 0)
        self.groupby_combo = QComboBox()
        self.groupby_combo.addItem("None")
        layout.addWidget(self.groupby_combo, 4, 1)
        
        # Run analysis button
        self.run_stats_btn = QPushButton("📊 Run Statistical Analysis")
        self.run_stats_btn.clicked.connect(self.run_statistical_analysis)
        layout.addWidget(self.run_stats_btn, 5, 0, 1, 2)
        
        return group
        
    def create_regression_group(self):
        """Create regression analysis controls."""
        group = QGroupBox("📉 Regression Analysis")
        layout = QGridLayout(group)
        
        # Regression type
        layout.addWidget(QLabel("Regression Type:"), 0, 0)
        self.regression_type_combo = QComboBox()
        self.regression_type_combo.addItems([
            "Linear Regression",
            "Polynomial Regression",
            "Ridge Regression",
            "Lasso Regression"
        ])
        layout.addWidget(self.regression_type_combo, 0, 1)
        
        # Independent variable (X)
        layout.addWidget(QLabel("X Variable:"), 1, 0)
        self.x_var_combo = QComboBox()
        layout.addWidget(self.x_var_combo, 1, 1)
        
        # Dependent variable (Y)
        layout.addWidget(QLabel("Y Variable:"), 2, 0)
        self.y_var_combo = QComboBox()
        layout.addWidget(self.y_var_combo, 2, 1)
        
        # Polynomial degree (for polynomial regression)
        layout.addWidget(QLabel("Polynomial Degree:"), 3, 0)
        self.poly_degree_spin = QSpinBox()
        self.poly_degree_spin.setRange(1, 10)
        self.poly_degree_spin.setValue(2)
        layout.addWidget(self.poly_degree_spin, 3, 1)
        
        # Regularization parameter (for Ridge/Lasso)
        layout.addWidget(QLabel("Regularization α:"), 4, 0)
        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setRange(0.001, 1000.0)
        self.alpha_spin.setValue(1.0)
        self.alpha_spin.setDecimals(3)
        layout.addWidget(self.alpha_spin, 4, 1)
        
        # Generate prediction data
        self.generate_predictions_check = QCheckBox("Generate Prediction Data")
        self.generate_predictions_check.setChecked(True)
        layout.addWidget(self.generate_predictions_check, 5, 0, 1, 2)
        
        # Run regression button
        self.run_regression_btn = QPushButton("📈 Run Regression Analysis")
        self.run_regression_btn.clicked.connect(self.run_regression_analysis)
        layout.addWidget(self.run_regression_btn, 6, 0, 1, 2)
        
        # Regression history and management
        layout.addWidget(QLabel("Saved Regressions:"), 7, 0)
        self.regression_history_combo = QComboBox()
        self.regression_history_combo.addItem("No regressions saved")
        self.regression_history_combo.currentTextChanged.connect(self.on_regression_selected)
        layout.addWidget(self.regression_history_combo, 7, 1)
        
        # Regression management buttons
        regression_btn_layout = QHBoxLayout()
        self.visualize_regression_btn = QPushButton("👁️ Visualize")
        self.visualize_regression_btn.clicked.connect(self.visualize_selected_regression)
        self.visualize_regression_btn.setEnabled(False)
        
        self.delete_regression_btn = QPushButton("🗑️ Delete")
        self.delete_regression_btn.clicked.connect(self.delete_selected_regression)
        self.delete_regression_btn.setEnabled(False)
        
        self.export_regression_btn = QPushButton("💾 Export")
        self.export_regression_btn.clicked.connect(self.export_selected_regression)
        self.export_regression_btn.setEnabled(False)
        
        regression_btn_layout.addWidget(self.visualize_regression_btn)
        regression_btn_layout.addWidget(self.delete_regression_btn)
        regression_btn_layout.addWidget(self.export_regression_btn)
        layout.addLayout(regression_btn_layout, 8, 0, 1, 2)
        
        return group
        
    def create_transformation_group(self):
        """Create data transformation controls."""
        group = QGroupBox("🔄 Data Transformations")
        layout = QGridLayout(group)
        
        # Transformation type
        layout.addWidget(QLabel("Transformation:"), 0, 0)
        self.transform_combo = QComboBox()
        self.transform_combo.addItems([
            "Logarithmic (log)",
            "Square Root (sqrt)", 
            "Power Transform",
            "Z-Score Standardization",
            "Min-Max Normalization",
            "Robust Scaling",
            "Box-Cox Transform",
            "Differencing"
        ])
        layout.addWidget(self.transform_combo, 0, 1)
        
        # Columns to transform
        layout.addWidget(QLabel("Transform Columns:"), 1, 0)
        self.transform_columns_list = QListWidget()
        self.transform_columns_list.setMaximumHeight(80)
        self.transform_columns_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(self.transform_columns_list, 1, 1, 2, 1)
        
        # Power parameter (for power transform)
        layout.addWidget(QLabel("Power (λ):"), 3, 0)
        self.power_spin = QDoubleSpinBox()
        self.power_spin.setRange(-5.0, 5.0)
        self.power_spin.setValue(2.0)
        self.power_spin.setDecimals(2)
        layout.addWidget(self.power_spin, 3, 1)
        
        # Run transformation button
        self.run_transform_btn = QPushButton("🔄 Apply Transformation")
        self.run_transform_btn.clicked.connect(self.run_transformation)
        layout.addWidget(self.run_transform_btn, 4, 0, 1, 2)
        
        # Transformation history and management
        layout.addWidget(QLabel("Saved Transformations:"), 5, 0)
        self.transformation_history_combo = QComboBox()
        self.transformation_history_combo.addItem("No transformations saved")
        self.transformation_history_combo.currentTextChanged.connect(self.on_transformation_selected)
        layout.addWidget(self.transformation_history_combo, 5, 1)
        
        # Transformation management buttons
        transform_btn_layout = QHBoxLayout()
        self.view_transformation_btn = QPushButton("👁️ View")
        self.view_transformation_btn.clicked.connect(self.view_selected_transformation)
        self.view_transformation_btn.setEnabled(False)
        
        self.delete_transformation_btn = QPushButton("🗑️ Delete")
        self.delete_transformation_btn.clicked.connect(self.delete_selected_transformation)
        self.delete_transformation_btn.setEnabled(False)
        
        self.export_transformation_btn = QPushButton("💾 Export")
        self.export_transformation_btn.clicked.connect(self.export_selected_transformation)
        self.export_transformation_btn.setEnabled(False)
        
        transform_btn_layout.addWidget(self.view_transformation_btn)
        transform_btn_layout.addWidget(self.delete_transformation_btn)
        transform_btn_layout.addWidget(self.export_transformation_btn)
        layout.addLayout(transform_btn_layout, 6, 0, 1, 2)
        
        return group
        
    def create_export_group(self):
        """Create export and save controls."""
        group = QGroupBox("💾 Export & Save")
        layout = QVBoxLayout(group)
        
        # Save generated data
        self.save_data_btn = QPushButton("💾 Save Generated Data")
        self.save_data_btn.clicked.connect(self.save_generated_data)
        layout.addWidget(self.save_data_btn)
        
        # Export results
        self.export_results_btn = QPushButton("📄 Export Analysis Results")
        self.export_results_btn.clicked.connect(self.export_analysis_results)
        layout.addWidget(self.export_results_btn)
        
        # Add to main dataset
        self.add_to_main_btn = QPushButton("➕ Add to Main Dataset")
        self.add_to_main_btn.clicked.connect(self.add_to_main_dataset)
        layout.addWidget(self.add_to_main_btn)
        
        return group
        
    def create_results_panel(self):
        """Create the results and visualization panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tab widget for different result views
        self.results_tabs = QTabWidget()
        
        # Statistical Results Tab
        self.stats_results_tab = self.create_stats_results_tab()
        self.results_tabs.addTab(self.stats_results_tab, "📊 Statistics")
        
        # Visualization Tab
        self.viz_tab = self.create_visualization_tab()
        self.results_tabs.addTab(self.viz_tab, "📈 Visualization")
        
        # Analysis Manager Tab
        self.analysis_manager_tab = self.create_analysis_manager_tab()
        self.results_tabs.addTab(self.analysis_manager_tab, "🔍 Analysis Manager")
        
        # Generated Data Tab
        self.data_tab = self.create_generated_data_tab()
        self.results_tabs.addTab(self.data_tab, "📋 Generated Data")
        
        # Analysis Summary Tab
        self.summary_tab = self.create_summary_tab()
        self.results_tabs.addTab(self.summary_tab, "📑 Summary")
        
        layout.addWidget(self.results_tabs)
        
        # Status and progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready for statistical analysis...")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)
        
        return widget
        
    def create_stats_results_tab(self):
        """Create the statistical results display tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setAlternatingRowColors(True)
        layout.addWidget(self.results_table)
        
        # Statistical summary text
        self.summary_text = QTextEdit()
        self.summary_text.setMaximumHeight(150)
        self.summary_text.setReadOnly(True)
        layout.addWidget(self.summary_text)
        
        return widget
        
    def create_visualization_tab(self):
        """Create the visualization tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Matplotlib figure and canvas
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        return widget
    
    def create_analysis_manager_tab(self):
        """Create the analysis manager tab for viewing multiple analyses simultaneously."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Analysis selection and comparison
        selection_layout = QHBoxLayout()
        
        # Regression selection
        regression_group = QGroupBox("📈 Regressions")
        regression_layout = QVBoxLayout(regression_group)
        
        self.regression_manager_list = QListWidget()
        self.regression_manager_list.setMaximumHeight(150)
        self.regression_manager_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.regression_manager_list.itemChanged.connect(self.on_analysis_selection_changed)  # Changed to itemChanged for checkboxes
        regression_layout.addWidget(self.regression_manager_list)
        
        regression_btn_layout = QHBoxLayout()
        self.compare_regressions_btn = QPushButton("📊 Compare Selected")
        self.compare_regressions_btn.clicked.connect(self.compare_selected_regressions)
        self.compare_regressions_btn.setEnabled(False)
        
        self.overlay_regressions_btn = QPushButton("🔄 Overlay Plot")
        self.overlay_regressions_btn.clicked.connect(self.overlay_selected_regressions)
        self.overlay_regressions_btn.setEnabled(False)
        
        regression_btn_layout.addWidget(self.compare_regressions_btn)
        regression_btn_layout.addWidget(self.overlay_regressions_btn)
        regression_layout.addLayout(regression_btn_layout)
        
        selection_layout.addWidget(regression_group)
        
        # Transformation selection
        transform_group = QGroupBox("🔄 Transformations")
        transform_layout = QVBoxLayout(transform_group)
        
        self.transformation_manager_list = QListWidget()
        self.transformation_manager_list.setMaximumHeight(150)
        self.transformation_manager_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.transformation_manager_list.itemChanged.connect(self.on_analysis_selection_changed)  # Changed to itemChanged for checkboxes
        transform_layout.addWidget(self.transformation_manager_list)
        
        transform_btn_layout = QHBoxLayout()
        self.compare_transformations_btn = QPushButton("📊 Compare Selected")
        self.compare_transformations_btn.clicked.connect(self.compare_selected_transformations)
        self.compare_transformations_btn.setEnabled(False)
        
        self.view_transformation_data_btn = QPushButton("👁️ View Data")
        self.view_transformation_data_btn.clicked.connect(self.view_selected_transformation_data)
        self.view_transformation_data_btn.setEnabled(False)
        
        transform_btn_layout.addWidget(self.compare_transformations_btn)
        transform_btn_layout.addWidget(self.view_transformation_data_btn)
        transform_layout.addLayout(transform_btn_layout)
        
        selection_layout.addWidget(transform_group)
        
        layout.addLayout(selection_layout)
        
        # Analysis comparison area
        comparison_group = QGroupBox("📊 Analysis Comparison")
        comparison_layout = QVBoxLayout(comparison_group)
        
        # Comparison results table
        self.comparison_table = QTableWidget()
        self.comparison_table.setAlternatingRowColors(True)
        comparison_layout.addWidget(self.comparison_table)
        
        # Comparison visualization area
        self.comparison_figure = Figure(figsize=(12, 6), dpi=100)
        self.comparison_canvas = FigureCanvas(self.comparison_figure)
        comparison_layout.addWidget(self.comparison_canvas)
        
        layout.addWidget(comparison_group)
        
        return widget
        
    def create_generated_data_tab(self):
        """Create the generated data display tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Generated datasets list
        layout.addWidget(QLabel("Generated Datasets:"))
        self.generated_data_list = QListWidget()
        self.generated_data_list.itemClicked.connect(self.show_generated_data)
        layout.addWidget(self.generated_data_list)
        
        # Data preview table
        self.data_preview_table = QTableWidget()
        self.data_preview_table.setAlternatingRowColors(True)
        layout.addWidget(self.data_preview_table)
        
        return widget
        
    def create_summary_tab(self):
        """Create the analysis summary tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Analysis history and metadata
        self.analysis_history = QTextEdit()
        self.analysis_history.setReadOnly(True)
        layout.addWidget(self.analysis_history)
        
        return widget
        
    def populate_measures_list(self):
        """Populate the statistical measures list using available statistics from descriptive module."""
        # Get available statistics from the descriptive statistics module
        available_stats = self.descriptive_stats.get_available_statistics()
        
        # Map internal names to display names
        display_names = {
            'count': 'Count',
            'mean': 'Mean',
            'median': 'Median',
            'mode': 'Mode',
            'std': 'Standard Deviation',
            'variance': 'Variance',
            'min': 'Minimum',
            'max': 'Maximum',
            'range': 'Range',
            'iqr': 'Interquartile Range',
            'q1': 'First Quartile',
            'q3': 'Third Quartile',
            'skewness': 'Skewness',
            'kurtosis': 'Kurtosis',
            'sem': 'Standard Error of Mean',
            'sum': 'Sum'
        }
        
        # Default checked measures
        default_checked = ['mean', 'std', 'median', 'count']
        
        for stat_name in available_stats:
            display_name = display_names.get(stat_name, stat_name.title())
            item = QListWidgetItem(display_name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if stat_name in default_checked else Qt.CheckState.Unchecked)
            # Store the internal name as data for easy retrieval
            item.setData(Qt.ItemDataRole.UserRole, stat_name)
            self.measures_list.addItem(item)
            
    def update_column_lists(self):
        """Update column selection dropdowns when new data is loaded."""
        if not self.data_manager.has_data():
            self.setEnabled(False)
            return
            
        self.setEnabled(True)
        
        # Get available datasets
        datasets = ['Current Data']  # Default to current data
        self.primary_data_combo.clear()
        self.primary_data_combo.addItems(datasets)
        
        # Update column lists
        self.update_columns_for_dataset()
        
    def update_columns_for_dataset(self):
        """Update column lists based on selected dataset."""
        if not self.data_manager.has_data():
            return
            
        data = self.data_manager.get_data()
        columns = list(data.columns)
        numeric_columns = list(data.select_dtypes(include=[np.number]).columns)
        
        # Update various column selectors
        self.columns_list.clear()
        for col in columns:
            item = QListWidgetItem(col)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if col in numeric_columns[:3] else Qt.CheckState.Unchecked)
            self.columns_list.addItem(item)
            
        # Update combo boxes
        for combo in [self.x_var_combo, self.y_var_combo, self.groupby_combo]:
            combo.clear()
            if combo == self.groupby_combo:
                combo.addItem("None")
            combo.addItems(numeric_columns if combo != self.groupby_combo else columns)
            
        # Update transform columns list
        self.transform_columns_list.clear()
        for col in numeric_columns:
            item = QListWidgetItem(col)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.transform_columns_list.addItem(item)
            
        # Analyze data relationships
        self.analyze_data_relationships()
        
    def on_primary_data_changed(self):
        """Handle primary dataset change."""
        self.update_columns_for_dataset()
        
    def on_stats_type_changed(self):
        """Handle statistics type change."""
        stats_type = self.stats_type_combo.currentText()
        # Update available measures based on selected type
        
    def analyze_data_relationships(self):
        """Analyze relationships between datasets."""
        self.related_data_tree.clear()
        # This will be expanded when multiple datasets are supported
        
    def get_selected_columns(self):
        """Get selected columns from the columns list."""
        selected = []
        for i in range(self.columns_list.count()):
            item = self.columns_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        return selected
        
    def get_selected_measures(self):
        """Get selected statistical measures (internal names)."""
        selected = []
        for i in range(self.measures_list.count()):
            item = self.measures_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                # Get the internal name stored as UserRole data
                internal_name = item.data(Qt.ItemDataRole.UserRole)
                if internal_name:
                    selected.append(internal_name)
                else:
                    # Fallback to text mapping if no data stored
                    text = item.text().lower().replace(' ', '_')
                    if 'standard deviation' in item.text().lower():
                        selected.append('std')
                    elif 'minimum' in item.text().lower():
                        selected.append('min')
                    elif 'maximum' in item.text().lower():
                        selected.append('max')
                    elif 'interquartile range' in item.text().lower():
                        selected.append('iqr')
                    elif 'first quartile' in item.text().lower():
                        selected.append('q1')
                    elif 'third quartile' in item.text().lower():
                        selected.append('q3')
                    elif 'standard error of mean' in item.text().lower():
                        selected.append('sem')
                    else:
                        selected.append(item.text().lower())
        return selected
        
    def get_selected_transform_columns(self):
        """Get selected columns for transformation."""
        selected = []
        for i in range(self.transform_columns_list.count()):
            item = self.transform_columns_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        return selected
        
    # Placeholder methods for analysis functions
    def run_statistical_analysis(self):
        """Run comprehensive statistical analysis using modular statistics classes."""
        try:
            self.status_label.setText("Running statistical analysis...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            data = self.data_manager.get_data()
            selected_columns = self.get_selected_columns()
            selected_measures = self.get_selected_measures()
            
            if not selected_columns:
                QMessageBox.warning(self, "Warning", "Please select at least one column for analysis.")
                return
                
            if not selected_measures:
                QMessageBox.warning(self, "Warning", "Please select at least one statistical measure.")
                return
                
            self.progress_bar.setValue(25)
            
            # Check if descriptive statistics is selected in the analysis type
            analysis_type = self.stats_type_combo.currentText()
            if analysis_type != "Descriptive Statistics":
                QMessageBox.information(self, "Info", 
                    "Currently only descriptive statistics are supported in this analysis.\n"
                    "Use the Regression and Transformation tabs for other analyses.")
                return
            
            # Compute selected descriptive statistics for selected columns only
            results = {}
            total_columns = len(selected_columns)
            
            for i, col in enumerate(selected_columns):
                if col in data.columns and pd.api.types.is_numeric_dtype(data[col]):
                    col_data = data[col]
                    
                    # Use the new descriptive statistics module
                    # Only calculate the selected measures
                    col_results = self.descriptive_stats.calculate_selected_stats(col_data, selected_measures)
                    results[col] = col_results
                    
                    # Update progress
                    progress = 25 + int((i + 1) / total_columns * 50)
                    self.progress_bar.setValue(progress)
                else:
                    # Skip non-numeric columns
                    QMessageBox.warning(self, "Warning", f"Column '{col}' is not numeric and will be skipped.")
            
            self.progress_bar.setValue(75)
            
            if not results:
                QMessageBox.warning(self, "Warning", "No numeric columns were analyzed.")
                return
            
            # Display results in table
            self.display_statistical_results(results, selected_measures)
            
            # Store results for potential export
            self.analysis_results['descriptive'] = {
                'data': results,
                'measures': selected_measures,
                'columns': selected_columns,
                'timestamp': pd.Timestamp.now()
            }
            
            self.progress_bar.setValue(100)
            self.status_label.setText(f"Statistical analysis completed: {len(results)} columns, {len(selected_measures)} measures")
            
            # Update analysis summary
            self.update_analysis_summary()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Statistical analysis failed: {str(e)}")
            self.status_label.setText("Analysis failed")
        finally:
            self.progress_bar.setVisible(False)
            
    def display_statistical_results(self, results, selected_measures=None):
        """Display statistical results in the table."""
        if not results:
            return
        
        # If no specific measures provided, use all available from results
        if selected_measures is None:
            if results:
                selected_measures = list(next(iter(results.values())).keys())
            else:
                return
        
        # Map internal names back to display names for table headers
        display_names = {
            'count': 'Count',
            'mean': 'Mean',
            'median': 'Median',
            'mode': 'Mode',
            'std': 'Standard Deviation',
            'variance': 'Variance',
            'min': 'Minimum',
            'max': 'Maximum',
            'range': 'Range',
            'iqr': 'Interquartile Range',
            'q1': 'First Quartile',
            'q3': 'Third Quartile',
            'skewness': 'Skewness',
            'kurtosis': 'Kurtosis',
            'sem': 'Standard Error of Mean',
            'sum': 'Sum'
        }
        
        # Prepare table
        columns = list(results.keys())
        display_measures = [display_names.get(measure, measure.title()) for measure in selected_measures]
        
        self.results_table.setRowCount(len(selected_measures))
        self.results_table.setColumnCount(len(columns) + 1)
        
        # Set headers
        headers = ['Measure'] + columns
        self.results_table.setHorizontalHeaderLabels(headers)
        
        # Fill table with only selected measures
        for i, measure in enumerate(selected_measures):
            # Set measure name (display name)
            display_measure = display_names.get(measure, measure.title())
            self.results_table.setItem(i, 0, QTableWidgetItem(display_measure))
            
            # Set values for each column
            for j, col in enumerate(columns):
                if measure in results[col]:
                    value = results[col][measure]
                    if isinstance(value, float):
                        text = f"{value:.4f}"
                    elif isinstance(value, int):
                        text = str(value)
                    else:
                        text = str(value)
                else:
                    text = "N/A"
                self.results_table.setItem(i, j + 1, QTableWidgetItem(text))
        
        # Auto-resize columns
        self.results_table.resizeColumnsToContents()
        
        # Update summary text
        summary = f"Statistical Analysis Summary\n"
        summary += f"Analyzed {len(columns)} columns with {len(selected_measures)} measures\n"
        if results and columns:
            first_col_results = results[columns[0]]
            if 'count' in first_col_results:
                summary += f"Total data points per column: {first_col_results['count']}\n"
        # Filter out None values before joining
        valid_display_measures = [name for name in display_measures if name is not None]
        summary += f"Selected measures: {', '.join(valid_display_measures)}\n"
        self.summary_text.setText(summary)
            
    def run_regression_analysis(self):
        """Run regression analysis using modular regression class and generate prediction data."""
        try:
            self.status_label.setText("Running regression analysis...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            data = self.data_manager.get_data()
            x_col = self.x_var_combo.currentText()
            y_col = self.y_var_combo.currentText()
            
            if not x_col or not y_col or x_col == y_col:
                QMessageBox.warning(self, "Warning", "Please select different X and Y variables.")
                return
                
            if x_col not in data.columns or y_col not in data.columns:
                QMessageBox.warning(self, "Warning", "Selected columns not found in data.")
                return
                
            self.progress_bar.setValue(25)
            
            # Prepare data
            # Align data (remove NaN pairs)
            valid_mask = ~(pd.isna(data[x_col]) | pd.isna(data[y_col]))
            x_clean = data.loc[valid_mask, x_col].values
            y_clean = data.loc[valid_mask, y_col].values
            
            if len(x_clean) < 2:
                QMessageBox.warning(self, "Warning", "Insufficient data points for regression.")
                return
                
            self.progress_bar.setValue(50)
            
            # Get regression type from UI
            regression_type_text = self.regression_type_combo.currentText()
            regression_type_map = {
                "Linear Regression": "linear",
                "Polynomial Regression": "polynomial",
                "Ridge Regression": "ridge",
                "Lasso Regression": "lasso"
            }
            regression_type = regression_type_map.get(regression_type_text, "linear")
            
            # Use the modular regression analysis class
            kwargs = {}
            if regression_type == "polynomial":
                kwargs['degree'] = self.poly_degree_spin.value()
            elif regression_type in ["ridge", "lasso"]:
                kwargs['alpha'] = self.alpha_spin.value()
            
            regression_results = self.regression_analysis.perform_regression(
                x_clean, y_clean, model_type=regression_type, **kwargs
            )
            
            self.progress_bar.setValue(75)
            
            # Generate and store datasets if requested
            if self.generate_predictions_check.isChecked():
                # Create regression datasets using the modular class
                datasets = self.regression_analysis.create_regression_datasets(
                    regression_results, x_col, y_col
                )
                
                # Store all generated datasets
                for dataset_type, dataset_df in datasets.items():
                    dataset_name = f"Regression_{x_col}_vs_{y_col}_{dataset_type}"
                    self.generated_datasets[dataset_name] = dataset_df
                    
                    # Emit signal for main application
                    self.data_created.emit(dataset_name, dataset_df)
                
                # Update generated data list
                self.update_generated_data_list()
            
            # Save regression to history with a unique name
            timestamp = pd.Timestamp.now()
            regression_name = f"{regression_type_text}: {x_col} vs {y_col} ({timestamp.strftime('%H:%M:%S')})"
            
            self.regression_history[regression_name] = {
                'results': regression_results,
                'x_column': x_col,
                'y_column': y_col,
                'regression_type': regression_type,
                'regression_type_text': regression_type_text,
                'timestamp': timestamp,
                'parameters': {
                    'degree': self.poly_degree_spin.value() if regression_type == "polynomial" else None,
                    'alpha': self.alpha_spin.value() if regression_type in ["ridge", "lasso"] else None
                }
            }
            
            # Update regression history dropdown
            self.update_regression_history_combo()
                
            # Store regression results for potential export
            self.analysis_results['regression'] = {
                'results': regression_results,
                'x_column': x_col,
                'y_column': y_col,
                'timestamp': timestamp
            }
            
            # Visualize regression using the new results
            self.visualize_regression_results_modular(regression_results, x_col, y_col)
            
            self.progress_bar.setValue(100)
            
            # Generate summary from modular class
            report = self.regression_analysis.generate_regression_report(regression_results)
            self.status_label.setText(
                f"Regression completed: R² = {regression_results['r_squared']:.4f}, "
                f"RMSE = {regression_results['rmse']:.4f}"
            )
            
            # Update analysis summary
            self.update_analysis_summary()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Regression analysis failed: {str(e)}")
            self.status_label.setText("Regression analysis failed")
        finally:
            self.progress_bar.setVisible(False)
            
    def visualize_regression_results_modular(self, regression_results, x_col, y_col):
        """Visualize regression results using modular regression output."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Get the original data to plot scatter points
        data = self.data_manager.get_data()
        valid_mask = ~(pd.isna(data[x_col]) | pd.isna(data[y_col]))
        x_original = data.loc[valid_mask, x_col].values
        y_original = data.loc[valid_mask, y_col].values
        
        # Scatter plot of original data
        ax.scatter(x_original, y_original, alpha=0.6, color='blue', label='Data Points')
        
        # Extract data from regression results
        x_smooth = regression_results['x_smooth']
        y_smooth = regression_results['y_smooth']
        r2 = regression_results['r_squared']
        
        # Regression line
        ax.plot(x_smooth, y_smooth, color='red', linewidth=2, 
                label=f'{regression_results["model_type"]} (R² = {r2:.3f})')
        
        # Add confidence intervals if available
        if 'ci_lower' in regression_results and 'ci_upper' in regression_results:
            ax.fill_between(x_smooth, regression_results['ci_lower'], 
                           regression_results['ci_upper'], alpha=0.2, color='red',
                           label='95% Confidence Interval')
        
        # Labels and title
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f'{regression_results["model_type"]}: {y_col} vs {x_col}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add equation text
        if 'slope' in regression_results and 'intercept' in regression_results:
            slope = regression_results['slope']
            intercept = regression_results['intercept']
            if isinstance(slope, (int, float)):
                equation = f'y = {slope:.4f}x + {intercept:.4f}'
            else:
                equation = f'Coefficients: {slope}'
            ax.text(0.05, 0.95, equation, transform=ax.transAxes, 
                    bbox=dict(boxstyle="round", facecolor='wheat'), verticalalignment='top')
        
        self.figure.tight_layout()
        self.canvas.draw()
        
        # Switch to visualization tab
        self.results_tabs.setCurrentIndex(1)
    
    def update_regression_history_combo(self):
        """Update the regression history dropdown."""
        self.regression_history_combo.clear()
        
        if not self.regression_history:
            self.regression_history_combo.addItem("No regressions saved")
            self.visualize_regression_btn.setEnabled(False)
            self.delete_regression_btn.setEnabled(False)
            self.export_regression_btn.setEnabled(False)
        else:
            # Sort by timestamp (newest first)
            sorted_regressions = sorted(
                self.regression_history.items(),
                key=lambda x: x[1]['timestamp'],
                reverse=True
            )
            
            for regression_name, _ in sorted_regressions:
                self.regression_history_combo.addItem(regression_name)
                
            self.visualize_regression_btn.setEnabled(True)
            self.delete_regression_btn.setEnabled(True)
            self.export_regression_btn.setEnabled(True)
            
        # Update analysis manager
        self.update_analysis_manager_lists()
    
    def on_regression_selected(self, regression_name):
        """Handle regression selection from dropdown."""
        if regression_name and regression_name != "No regressions saved":
            self.visualize_regression_btn.setEnabled(True)
            self.delete_regression_btn.setEnabled(True)
            self.export_regression_btn.setEnabled(True)
        else:
            self.visualize_regression_btn.setEnabled(False)
            self.delete_regression_btn.setEnabled(False)
            self.export_regression_btn.setEnabled(False)
    
    def visualize_selected_regression(self):
        """Visualize the selected regression from history."""
        regression_name = self.regression_history_combo.currentText()
        
        if regression_name in self.regression_history:
            regression_data = self.regression_history[regression_name]
            self.visualize_regression_results_modular(
                regression_data['results'],
                regression_data['x_column'],
                regression_data['y_column']
            )
            
            # Update status
            r2 = regression_data['results']['r_squared']
            rmse = regression_data['results']['rmse']
            self.status_label.setText(
                f"Viewing {regression_data['regression_type_text']}: "
                f"R² = {r2:.4f}, RMSE = {rmse:.4f}"
            )
    
    def delete_selected_regression(self):
        """Delete the selected regression from history."""
        regression_name = self.regression_history_combo.currentText()
        
        if regression_name in self.regression_history:
            reply = QMessageBox.question(
                self, "Delete Regression",
                f"Are you sure you want to delete the regression:\n{regression_name}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                del self.regression_history[regression_name]
                self.update_regression_history_combo()
                self.status_label.setText("Regression deleted")
    
    def export_selected_regression(self):
        """Export the selected regression results to file."""
        regression_name = self.regression_history_combo.currentText()
        
        if regression_name in self.regression_history:
            regression_data = self.regression_history[regression_name]
            
            # Create detailed report
            report = self.regression_analysis.generate_regression_report(
                regression_data['results']
            )
            
            # Add additional information
            detailed_report = f"""
Regression Analysis Report
========================

Analysis: {regression_name}
Timestamp: {regression_data['timestamp']}
X Variable: {regression_data['x_column']}
Y Variable: {regression_data['y_column']}
Regression Type: {regression_data['regression_type_text']}

{report}

Parameters Used:
"""
            
            # Add parameters if available
            if regression_data['parameters']:
                for param, value in regression_data['parameters'].items():
                    if value is not None:
                        detailed_report += f"- {param}: {value}\n"
            
            # Save to file
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Regression Report",
                f"regression_report_{regression_data['timestamp'].strftime('%Y%m%d_%H%M%S')}.txt",
                "Text files (*.txt);;All files (*.*)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'w') as f:
                        f.write(detailed_report)
                    self.status_label.setText(f"Regression report exported to {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Export Error", f"Failed to export report: {str(e)}")
    
    def update_transformation_history_combo(self):
        """Update the transformation history dropdown."""
        self.transformation_history_combo.clear()
        
        if not self.transformation_history:
            self.transformation_history_combo.addItem("No transformations saved")
            self.view_transformation_btn.setEnabled(False)
            self.delete_transformation_btn.setEnabled(False)
            self.export_transformation_btn.setEnabled(False)
        else:
            # Sort by timestamp (newest first)
            sorted_transformations = sorted(
                self.transformation_history.items(),
                key=lambda x: x[1]['timestamp'],
                reverse=True
            )
            
            for transform_name, _ in sorted_transformations:
                self.transformation_history_combo.addItem(transform_name)
                
            self.view_transformation_btn.setEnabled(True)
            self.delete_transformation_btn.setEnabled(True)
            self.export_transformation_btn.setEnabled(True)
            
        # Update analysis manager
        self.update_analysis_manager_lists()
    
    def on_transformation_selected(self, transform_name):
        """Handle transformation selection from dropdown."""
        if transform_name and transform_name != "No transformations saved":
            self.view_transformation_btn.setEnabled(True)
            self.delete_transformation_btn.setEnabled(True)
            self.export_transformation_btn.setEnabled(True)
        else:
            self.view_transformation_btn.setEnabled(False)
            self.delete_transformation_btn.setEnabled(False)
            self.export_transformation_btn.setEnabled(False)
    
    def view_selected_transformation(self):
        """View the selected transformation from history."""
        transform_name = self.transformation_history_combo.currentText()
        
        if transform_name in self.transformation_history:
            transform_data = self.transformation_history[transform_name]
            
            # Show preview of the first transformed dataset
            if transform_data['datasets']:
                first_dataset = next(iter(transform_data['datasets'].values()))
                self.show_data_preview(first_dataset)
                
                # Update status
                num_datasets = len(transform_data['datasets'])
                columns = ', '.join(transform_data['columns'])
                self.status_label.setText(
                    f"Viewing {transform_data['transformation_type']}: "
                    f"{num_datasets} datasets for columns: {columns}"
                )
                
                # Update analysis history with transformation details
                info = f"Transformation: {transform_name}\n"
                info += f"Type: {transform_data['transformation_type']}\n"
                info += f"Columns: {columns}\n"
                info += f"Datasets created: {num_datasets}\n"
                info += f"Timestamp: {transform_data['timestamp']}\n\n"
                
                current_text = self.analysis_history.toPlainText()
                self.analysis_history.setText(current_text + info)
    
    def delete_selected_transformation(self):
        """Delete the selected transformation from history."""
        transform_name = self.transformation_history_combo.currentText()
        
        if transform_name in self.transformation_history:
            reply = QMessageBox.question(
                self, "Delete Transformation",
                f"Are you sure you want to delete the transformation:\n{transform_name}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Remove datasets from generated datasets as well
                transform_data = self.transformation_history[transform_name]
                for dataset_name in transform_data['datasets'].keys():
                    if dataset_name in self.generated_datasets:
                        del self.generated_datasets[dataset_name]
                
                del self.transformation_history[transform_name]
                self.update_transformation_history_combo()
                self.update_generated_data_list()
                self.status_label.setText("Transformation deleted")
    
    def export_selected_transformation(self):
        """Export the selected transformation results to file."""
        transform_name = self.transformation_history_combo.currentText()
        
        if transform_name in self.transformation_history:
            transform_data = self.transformation_history[transform_name]
            
            # Create detailed report
            detailed_report = f"""
Transformation Analysis Report
=============================

Analysis: {transform_name}
Timestamp: {transform_data['timestamp']}
Transformation Type: {transform_data['transformation_type']}
Columns Transformed: {', '.join(transform_data['columns'])}

Datasets Created:
"""
            
            for dataset_name, dataset_df in transform_data['datasets'].items():
                detailed_report += f"- {dataset_name}: {len(dataset_df)} rows × {len(dataset_df.columns)} columns\n"
            
            # Add parameters if available
            if transform_data['parameters']:
                detailed_report += "\nParameters Used:\n"
                for param, value in transform_data['parameters'].items():
                    if value is not None:
                        detailed_report += f"- {param}: {value}\n"
            
            # Save to file
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Transformation Report",
                f"transformation_report_{transform_data['timestamp'].strftime('%Y%m%d_%H%M%S')}.txt",
                "Text files (*.txt);;All files (*.*)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'w') as f:
                        f.write(detailed_report)
                    self.status_label.setText(f"Transformation report exported to {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Export Error", f"Failed to export report: {str(e)}")
    
    def update_analysis_manager_lists(self):
        """Update the analysis manager lists with current regressions and transformations."""
        # Check if the analysis manager widgets exist (they might not be created yet)
        if not hasattr(self, 'regression_manager_list') or not hasattr(self, 'transformation_manager_list'):
            return
        
        try:
            # Update regression manager list
            self.regression_manager_list.clear()
            for regression_name in self.regression_history.keys():
                item = QListWidgetItem(regression_name)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.regression_manager_list.addItem(item)
            
            # Update transformation manager list
            self.transformation_manager_list.clear()
            for transform_name in self.transformation_history.keys():
                item = QListWidgetItem(transform_name)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.transformation_manager_list.addItem(item)
        except Exception as e:
            # Silently handle any widget access issues
            pass
    
    def on_analysis_selection_changed(self):
        """Handle selection changes in analysis manager lists."""
        # Check regression selections
        selected_regressions = []
        for i in range(self.regression_manager_list.count()):
            item = self.regression_manager_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_regressions.append(item.text())
        
        # Check transformation selections
        selected_transformations = []
        for i in range(self.transformation_manager_list.count()):
            item = self.transformation_manager_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_transformations.append(item.text())
        
        # Enable/disable buttons based on selections
        self.compare_regressions_btn.setEnabled(len(selected_regressions) >= 2)
        self.overlay_regressions_btn.setEnabled(len(selected_regressions) >= 2)
        self.compare_transformations_btn.setEnabled(len(selected_transformations) >= 1)
        self.view_transformation_data_btn.setEnabled(len(selected_transformations) >= 1)
    
    def compare_selected_regressions(self):
        """Compare selected regressions in a table."""
        selected_regressions = []
        for i in range(self.regression_manager_list.count()):
            item = self.regression_manager_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_regressions.append(item.text())
        
        if len(selected_regressions) < 2:
            QMessageBox.warning(self, "Warning", "Please select at least 2 regressions to compare.")
            return
        
        # Create comparison table
        headers = ["Regression", "Type", "X Variable", "Y Variable", "R²", "RMSE", "Slope", "Intercept"]
        self.comparison_table.setRowCount(len(selected_regressions))
        self.comparison_table.setColumnCount(len(headers))
        self.comparison_table.setHorizontalHeaderLabels(headers)
        
        for i, regression_name in enumerate(selected_regressions):
            if regression_name in self.regression_history:
                data = self.regression_history[regression_name]
                results = data['results']
                
                self.comparison_table.setItem(i, 0, QTableWidgetItem(regression_name[:30] + "..."))
                self.comparison_table.setItem(i, 1, QTableWidgetItem(data['regression_type_text']))
                self.comparison_table.setItem(i, 2, QTableWidgetItem(data['x_column']))
                self.comparison_table.setItem(i, 3, QTableWidgetItem(data['y_column']))
                self.comparison_table.setItem(i, 4, QTableWidgetItem(f"{results['r_squared']:.4f}"))
                self.comparison_table.setItem(i, 5, QTableWidgetItem(f"{results['rmse']:.4f}"))
                
                if 'slope' in results and isinstance(results['slope'], (int, float)):
                    self.comparison_table.setItem(i, 6, QTableWidgetItem(f"{results['slope']:.4f}"))
                else:
                    self.comparison_table.setItem(i, 6, QTableWidgetItem("N/A"))
                
                if 'intercept' in results and isinstance(results['intercept'], (int, float)):
                    self.comparison_table.setItem(i, 7, QTableWidgetItem(f"{results['intercept']:.4f}"))
                else:
                    self.comparison_table.setItem(i, 7, QTableWidgetItem("N/A"))
        
        self.comparison_table.resizeColumnsToContents()
        
        # Switch to analysis manager tab
        self.results_tabs.setCurrentIndex(2)
        
        self.status_label.setText(f"Comparing {len(selected_regressions)} regressions")
    
    def overlay_selected_regressions(self):
        """Overlay selected regressions in a single plot."""
        selected_regressions = []
        for i in range(self.regression_manager_list.count()):
            item = self.regression_manager_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_regressions.append(item.text())
        
        if len(selected_regressions) < 2:
            QMessageBox.warning(self, "Warning", "Please select at least 2 regressions to overlay.")
            return
        
        # Clear the comparison figure
        self.comparison_figure.clear()
        ax = self.comparison_figure.add_subplot(111)
        
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
        
        # Plot original data once (from the first regression)
        first_regression = selected_regressions[0]
        if first_regression in self.regression_history:
            first_data = self.regression_history[first_regression]
            data = self.data_manager.get_data()
            x_col = first_data['x_column']
            y_col = first_data['y_column']
            
            valid_mask = ~(pd.isna(data[x_col]) | pd.isna(data[y_col]))
            x_original = data.loc[valid_mask, x_col].values
            y_original = data.loc[valid_mask, y_col].values
            
            ax.scatter(x_original, y_original, alpha=0.6, color='lightgray', label='Data Points', s=20)
        
        # Overlay each regression line
        for i, regression_name in enumerate(selected_regressions):
            if regression_name in self.regression_history:
                data = self.regression_history[regression_name]
                results = data['results']
                color = colors[i % len(colors)]
                
                # Extract smooth line data
                x_smooth = results['x_smooth']
                y_smooth = results['y_smooth']
                r2 = results['r_squared']
                
                # Plot regression line
                ax.plot(x_smooth, y_smooth, color=color, linewidth=2, 
                       label=f'{data["regression_type_text"]} (R² = {r2:.3f})')
        
        ax.set_xlabel(first_data['x_column'])
        ax.set_ylabel(first_data['y_column'])
        ax.set_title(f'Regression Comparison: {first_data["y_column"]} vs {first_data["x_column"]}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.comparison_figure.tight_layout()
        self.comparison_canvas.draw()
        
        # Switch to analysis manager tab
        self.results_tabs.setCurrentIndex(2)
        
        self.status_label.setText(f"Overlaying {len(selected_regressions)} regressions")
    
    def compare_selected_transformations(self):
        """Compare selected transformations."""
        selected_transformations = []
        for i in range(self.transformation_manager_list.count()):
            item = self.transformation_manager_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_transformations.append(item.text())
        
        if not selected_transformations:
            QMessageBox.warning(self, "Warning", "Please select at least 1 transformation to compare.")
            return
        
        # Create comparison table for transformations
        headers = ["Transformation", "Type", "Columns", "Datasets Created", "Timestamp"]
        self.comparison_table.setRowCount(len(selected_transformations))
        self.comparison_table.setColumnCount(len(headers))
        self.comparison_table.setHorizontalHeaderLabels(headers)
        
        for i, transform_name in enumerate(selected_transformations):
            if transform_name in self.transformation_history:
                data = self.transformation_history[transform_name]
                
                self.comparison_table.setItem(i, 0, QTableWidgetItem(transform_name[:30] + "..."))
                self.comparison_table.setItem(i, 1, QTableWidgetItem(data['transformation_type']))
                self.comparison_table.setItem(i, 2, QTableWidgetItem(', '.join(data['columns'])))
                self.comparison_table.setItem(i, 3, QTableWidgetItem(str(len(data['datasets']))))
                self.comparison_table.setItem(i, 4, QTableWidgetItem(data['timestamp'].strftime('%H:%M:%S')))
        
        self.comparison_table.resizeColumnsToContents()
        
        # Switch to analysis manager tab
        self.results_tabs.setCurrentIndex(2)
        
        self.status_label.setText(f"Comparing {len(selected_transformations)} transformations")
    
    def view_selected_transformation_data(self):
        """View data from selected transformations."""
        selected_transformations = []
        for i in range(self.transformation_manager_list.count()):
            item = self.transformation_manager_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_transformations.append(item.text())
        
        if not selected_transformations:
            QMessageBox.warning(self, "Warning", "Please select at least 1 transformation to view.")
            return
        
        # Show data from the first selected transformation
        transform_name = selected_transformations[0]
        if transform_name in self.transformation_history:
            transform_data = self.transformation_history[transform_name]
            
            if transform_data['datasets']:
                first_dataset = next(iter(transform_data['datasets'].values()))
                self.show_data_preview(first_dataset)
                
                self.status_label.setText(f"Viewing data from: {transform_name}")
        
    def run_transformation(self):
        """Run data transformation using modular transformation class and generate transformed data."""
        try:
            self.status_label.setText("Applying transformation...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            data = self.data_manager.get_data()
            selected_columns = self.get_selected_transform_columns()
            
            if not selected_columns:
                QMessageBox.warning(self, "Warning", "Please select at least one column to transform.")
                return
                
            transformation = self.transform_combo.currentText()
            
            # Map UI transformation names to internal names
            transform_mapping = {
                "Logarithmic (log)": "log",
                "Square Root (sqrt)": "sqrt",
                "Power Transform": "square",  # Will be customized
                "Z-Score Standardization": "zscore",
                "Min-Max Normalization": "normalize",
                "Box-Cox Transform": "box_cox",
                "Robust Scaling": "robust_scale"
            }
            
            transform_type = transform_mapping.get(transformation)
            if not transform_type:
                QMessageBox.warning(self, "Warning", f"Transformation '{transformation}' is not supported yet.")
                return
            
            self.progress_bar.setValue(25)
            
            # Apply transformations to selected columns
            transformed_datasets = {}
            total_columns = len(selected_columns)
            
            for i, col in enumerate(selected_columns):
                if col not in data.columns:
                    continue
                    
                col_data = data[col]
                if not pd.api.types.is_numeric_dtype(col_data):
                    QMessageBox.warning(self, "Warning", f"Column '{col}' is not numeric and will be skipped.")
                    continue
                    
                try:
                    # Handle special cases for transformations that need parameters
                    if transform_type == "square" and transformation == "Power Transform":
                        power = self.power_spin.value()
                        if power == 2:
                            transform_results = self.data_transformations.apply_transformation(col_data, "square")
                        else:
                            # For other powers, we'll just use square for now
                            transform_results = self.data_transformations.apply_transformation(col_data, "square")
                    else:
                        # Use the modular transformation class
                        transform_results = self.data_transformations.apply_transformation(col_data, transform_type)
                    
                    # Create dataset for this transformed column
                    transformed_df = self.data_transformations.create_transformation_dataset(
                        transform_results, col
                    )
                    
                    # Store the transformed dataset
                    dataset_name = f"Transform_{col}_{transform_type}"
                    transformed_datasets[dataset_name] = transformed_df
                    self.generated_datasets[dataset_name] = transformed_df
                    
                    # Emit signal for main application
                    self.data_created.emit(dataset_name, transformed_df)
                    
                    # Store transformation results for potential export
                    if 'transformations' not in self.analysis_results:
                        self.analysis_results['transformations'] = {}
                    self.analysis_results['transformations'][col] = {
                        'results': transform_results,
                        'transform_type': transform_type,
                        'timestamp': pd.Timestamp.now()
                    }
                    
                except Exception as e:
                    QMessageBox.warning(self, "Warning", f"Error transforming column {col}: {str(e)}")
                    continue
                
                # Update progress
                progress = 25 + int((i + 1) / total_columns * 50)
                self.progress_bar.setValue(progress)
            
            self.progress_bar.setValue(75)
            
            if not transformed_datasets:
                QMessageBox.warning(self, "Warning", "No columns were successfully transformed.")
                return
            
            # Save transformation to history with a unique name
            timestamp = pd.Timestamp.now()
            transform_name = f"{transformation}: {', '.join(selected_columns)} ({timestamp.strftime('%H:%M:%S')})"
            
            self.transformation_history[transform_name] = {
                'datasets': transformed_datasets,
                'transformation_type': transformation,
                'transform_type': transform_type,
                'columns': selected_columns,
                'timestamp': timestamp,
                'parameters': {
                    'power': self.power_spin.value() if transformation == "Power Transform" else None
                }
            }
            
            # Update transformation history dropdown
            self.update_transformation_history_combo()
            
            # Update generated data list
            self.update_generated_data_list()
            
            self.progress_bar.setValue(100)
            self.status_label.setText(f"Transformation completed: {len(transformed_datasets)} datasets created")
            
            # Update analysis summary
            self.update_analysis_summary()
            
            # Show preview of the first transformed dataset
            if transformed_datasets:
                first_dataset = next(iter(transformed_datasets.values()))
                self.show_data_preview(first_dataset)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Transformation failed: {str(e)}")
            self.status_label.setText("Transformation failed")
        finally:
            self.progress_bar.setVisible(False)
            
    def show_data_preview(self, dataframe):
        """Show a preview of the dataframe in the generated data tab."""
        # Set up the preview table
        self.data_preview_table.setRowCount(min(50, len(dataframe)))  # Show first 50 rows
        self.data_preview_table.setColumnCount(len(dataframe.columns))
        self.data_preview_table.setHorizontalHeaderLabels(list(dataframe.columns))
        
        # Fill the table
        for i in range(min(50, len(dataframe))):
            for j, col in enumerate(dataframe.columns):
                value = dataframe.iloc[i, j]
                if pd.isna(value):
                    text = "NaN"
                elif isinstance(value, float):
                    text = f"{value:.4f}"
                else:
                    text = str(value)
                self.data_preview_table.setItem(i, j, QTableWidgetItem(text))
        
        # Auto-resize columns
        self.data_preview_table.resizeColumnsToContents()
        
        # Switch to generated data tab (index 3)
        self.results_tabs.setCurrentIndex(3)
        
    def save_generated_data(self):
        """Save generated data to file."""
        if not self.generated_datasets:
            QMessageBox.information(self, "Info", "No generated datasets to save.")
            return
            
        # Get selected dataset
        current_item = self.generated_data_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a dataset to save.")
            return
            
        dataset_name = current_item.text()
        if dataset_name not in self.generated_datasets:
            QMessageBox.warning(self, "Warning", "Selected dataset not found.")
            return
            
        # Get save filename
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Generated Data", 
            f"{dataset_name}.csv", 
            "CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*)"
        )
        
        if filename:
            try:
                dataframe = self.generated_datasets[dataset_name]
                if filename.endswith('.xlsx'):
                    dataframe.to_excel(filename, index=False)
                else:
                    dataframe.to_csv(filename, index=False)
                    
                self.status_label.setText(f"Data saved to {filename}")
                QMessageBox.information(self, "Success", f"Dataset saved successfully to {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save data: {str(e)}")
        
    def export_analysis_results(self):
        """Export analysis results."""
        if not self.analysis_results:
            QMessageBox.information(self, "Info", "No analysis results to export.")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Analysis Results", 
            "analysis_results.txt", 
            "Text Files (*.txt);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("Statistical Analysis Results\n")
                    f.write("="*40 + "\n\n")
                    
                    for analysis_name, results in self.analysis_results.items():
                        f.write(f"{analysis_name}\n")
                        f.write("-" * len(analysis_name) + "\n")
                        f.write(str(results) + "\n\n")
                        
                self.status_label.setText(f"Results exported to {filename}")
                QMessageBox.information(self, "Success", f"Results exported successfully to {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export results: {str(e)}")
        
    def add_to_main_dataset(self):
        """Add generated data to main dataset."""
        current_item = self.generated_data_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a dataset to add to main data.")
            return
            
        dataset_name = current_item.text()
        if dataset_name not in self.generated_datasets:
            QMessageBox.warning(self, "Warning", "Selected dataset not found.")
            return
            
        try:
            # Get the generated dataset
            generated_data = self.generated_datasets[dataset_name]
            
            # Add columns to main dataset
            main_data = self.data_manager.get_data()
            
            # Find columns that don't exist in main data
            new_columns = [col for col in generated_data.columns if col not in main_data.columns]
            
            if not new_columns:
                QMessageBox.information(self, "Info", "No new columns to add - all columns already exist in main dataset.")
                return
                
            # Add new columns to main data
            for col in new_columns:
                if len(generated_data) == len(main_data):
                    main_data[col] = generated_data[col]
                else:
                    # Handle size mismatch
                    main_data[col] = np.nan
                    min_len = min(len(main_data), len(generated_data))
                    main_data.iloc[:min_len, main_data.columns.get_loc(col)] = generated_data[col].iloc[:min_len]
            
            # Update all tabs
            self.update_column_lists()
            # Signal other tabs to update as well
            self.data_created.emit("Updated_Main_Data", main_data)
            
            self.status_label.setText(f"Added {len(new_columns)} new columns to main dataset")
            QMessageBox.information(self, "Success", f"Successfully added {len(new_columns)} columns to main dataset:\n" + ", ".join(new_columns))
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add to main dataset: {str(e)}")
        
    def show_generated_data(self, item):
        """Show selected generated dataset."""
        dataset_name = item.text()
        if dataset_name in self.generated_datasets:
            dataframe = self.generated_datasets[dataset_name]
            
            # Update the data preview table without switching tabs
            if hasattr(self, 'data_preview_table'):
                # Clear existing table
                self.data_preview_table.setRowCount(0)
                self.data_preview_table.setColumnCount(0)
                
                # Fill the preview table
                if not dataframe.empty:
                    self.data_preview_table.setRowCount(min(100, len(dataframe)))  # Show max 100 rows
                    self.data_preview_table.setColumnCount(len(dataframe.columns))
                    self.data_preview_table.setHorizontalHeaderLabels(dataframe.columns.tolist())
                    
                    for i in range(min(100, len(dataframe))):
                        for j, col in enumerate(dataframe.columns):
                            value = str(dataframe.iloc[i, j])
                            if len(value) > 50:
                                value = value[:47] + "..."
                            self.data_preview_table.setItem(i, j, QTableWidgetItem(value))
                    
                    self.data_preview_table.resizeColumnsToContents()
            
            # Update analysis history
            info = f"Dataset: {dataset_name}\n"
            info += f"Dimensions: {len(dataframe)} rows × {len(dataframe.columns)} columns\n"
            info += f"Columns: {', '.join(dataframe.columns)}\n"
            info += f"Memory usage: {dataframe.memory_usage(deep=True).sum() / 1024:.2f} KB\n\n"
            
            current_text = self.analysis_history.toPlainText()
            self.analysis_history.setText(current_text + info)
        
    def update_generated_data_list(self):
        """Update the list of generated datasets."""
        self.generated_data_list.clear()
        for name in self.generated_datasets.keys():
            self.generated_data_list.addItem(name)
        
        # Update analysis manager lists
        self.update_analysis_manager_lists()
        
        # Update summary tab
        self.update_analysis_summary()
    
    def update_analysis_summary(self):
        """Update the analysis summary tab with comprehensive information."""
        summary_text = "Statistical Analysis Session Summary\n"
        summary_text += "=" * 40 + "\n\n"
        
        # Session overview
        summary_text += f"Session Started: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary_text += f"Data Manager Status: {'Active' if self.data_manager.has_data() else 'No Data Loaded'}\n\n"
        
        # Data overview
        if self.data_manager.has_data():
            data = self.data_manager.get_data()
            summary_text += "Current Dataset Overview:\n"
            summary_text += f"- Rows: {len(data)}\n"
            summary_text += f"- Columns: {len(data.columns)}\n"
            summary_text += f"- Numeric Columns: {len(data.select_dtypes(include=[np.number]).columns)}\n"
            summary_text += f"- Non-Numeric Columns: {len(data.select_dtypes(exclude=[np.number]).columns)}\n"
            summary_text += f"- Missing Values: {data.isnull().sum().sum()}\n\n"
        
        # Regression Analysis Summary
        if self.regression_history:
            summary_text += f"Regression Analyses Performed: {len(self.regression_history)}\n"
            summary_text += "-" * 30 + "\n"
            
            for name, data in self.regression_history.items():
                results = data['results']
                summary_text += f"• {name}\n"
                summary_text += f"  Type: {data['regression_type_text']}\n"
                summary_text += f"  Variables: {data['x_column']} → {data['y_column']}\n"
                summary_text += f"  R²: {results['r_squared']:.4f}\n"
                summary_text += f"  RMSE: {results['rmse']:.4f}\n"
                summary_text += f"  Timestamp: {data['timestamp'].strftime('%H:%M:%S')}\n\n"
        else:
            summary_text += "No regression analyses performed yet.\n\n"
        
        # Transformation Analysis Summary
        if self.transformation_history:
            summary_text += f"Data Transformations Performed: {len(self.transformation_history)}\n"
            summary_text += "-" * 30 + "\n"
            
            for name, data in self.transformation_history.items():
                summary_text += f"• {name}\n"
                summary_text += f"  Type: {data['transformation_type']}\n"
                summary_text += f"  Columns: {', '.join(data['columns'])}\n"
                summary_text += f"  Datasets Created: {len(data['datasets'])}\n"
                summary_text += f"  Timestamp: {data['timestamp'].strftime('%H:%M:%S')}\n\n"
        else:
            summary_text += "No data transformations performed yet.\n\n"
        
        # Generated Datasets Summary
        if self.generated_datasets:
            summary_text += f"Generated Datasets: {len(self.generated_datasets)}\n"
            summary_text += "-" * 20 + "\n"
            
            for name, dataset in self.generated_datasets.items():
                summary_text += f"• {name}\n"
                summary_text += f"  Dimensions: {len(dataset)} × {len(dataset.columns)}\n"
                summary_text += f"  Columns: {', '.join(dataset.columns)}\n"
                summary_text += f"  Memory: {dataset.memory_usage(deep=True).sum() / 1024:.1f} KB\n\n"
        else:
            summary_text += "No datasets generated yet.\n\n"
        
        # Analysis Results Summary
        if self.analysis_results:
            summary_text += f"Analysis Results Available: {len(self.analysis_results)}\n"
            summary_text += "-" * 25 + "\n"
            
            for analysis_type, results in self.analysis_results.items():
                summary_text += f"• {analysis_type.title()} Analysis\n"
                if 'timestamp' in results:
                    summary_text += f"  Last Updated: {results['timestamp'].strftime('%H:%M:%S')}\n"
                if analysis_type == 'descriptive' and 'columns' in results:
                    summary_text += f"  Columns Analyzed: {len(results['columns'])}\n"
                    summary_text += f"  Measures Calculated: {len(results['measures'])}\n"
                summary_text += "\n"
        else:
            summary_text += "No analysis results available yet.\n\n"
        
        # Recommendations
        summary_text += "Recommendations:\n"
        summary_text += "-" * 15 + "\n"
        
        if not self.data_manager.has_data():
            summary_text += "• Load a dataset to begin analysis\n"
        elif not self.regression_history and not self.transformation_history:
            summary_text += "• Try running regression analysis or data transformations\n"
        elif self.regression_history and not self.transformation_history:
            summary_text += "• Consider data transformations to improve regression results\n"
        elif len(self.regression_history) == 1:
            summary_text += "• Compare multiple regression types using the Analysis Manager\n"
        else:
            summary_text += "• Use the Analysis Manager to compare and overlay your analyses\n"
        
        if self.generated_datasets:
            summary_text += "• Export your generated datasets or add them to the main dataset\n"
        
        self.analysis_history.setText(summary_text)
