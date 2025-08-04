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
            "Lasso Regression",
            "Exponential Fit",
            "Logarithmic Fit",
            "Power Law Fit"
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
        """Populate the statistical measures list."""
        basic_measures = [
            "Count", "Mean", "Median", "Mode", "Standard Deviation",
            "Variance", "Minimum", "Maximum", "Range", "Skewness", "Kurtosis"
        ]
        
        for measure in basic_measures:
            item = QListWidgetItem(measure)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if measure in ["Mean", "Standard Deviation", "Median"] else Qt.CheckState.Unchecked)
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
        """Get selected statistical measures."""
        selected = []
        for i in range(self.measures_list.count()):
            item = self.measures_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
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
        """Run comprehensive statistical analysis."""
        try:
            self.status_label.setText("Running statistical analysis...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            data = self.data_manager.get_data()
            selected_columns = self.get_selected_columns()
            
            if not selected_columns:
                QMessageBox.warning(self, "Warning", "Please select at least one column for analysis.")
                return
                
            self.progress_bar.setValue(25)
            
            # Compute basic descriptive statistics
            results = {}
            for col in selected_columns:
                if col in data.columns and pd.api.types.is_numeric_dtype(data[col]):
                    col_data = data[col].dropna()
                    results[col] = {
                        'Count': len(col_data),
                        'Mean': col_data.mean(),
                        'Median': col_data.median(),
                        'Std Dev': col_data.std(),
                        'Min': col_data.min(),
                        'Max': col_data.max(),
                        'Skewness': stats.skew(col_data) if len(col_data) > 1 else 0,
                        'Kurtosis': stats.kurtosis(col_data) if len(col_data) > 1 else 0
                    }
            
            self.progress_bar.setValue(75)
            
            # Display results in table
            self.display_statistical_results(results)
            
            self.progress_bar.setValue(100)
            self.status_label.setText("Statistical analysis completed successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Statistical analysis failed: {str(e)}")
            self.status_label.setText("Analysis failed")
        finally:
            self.progress_bar.setVisible(False)
            
    def display_statistical_results(self, results):
        """Display statistical results in the table."""
        if not results:
            return
            
        # Prepare table
        measures = list(next(iter(results.values())).keys())
        columns = list(results.keys())
        
        self.results_table.setRowCount(len(measures))
        self.results_table.setColumnCount(len(columns) + 1)
        
        # Set headers
        headers = ['Measure'] + columns
        self.results_table.setHorizontalHeaderLabels(headers)
        
        # Fill table
        for i, measure in enumerate(measures):
            self.results_table.setItem(i, 0, QTableWidgetItem(measure))
            for j, col in enumerate(columns):
                value = results[col][measure]
                if isinstance(value, float):
                    text = f"{value:.4f}"
                else:
                    text = str(value)
                self.results_table.setItem(i, j + 1, QTableWidgetItem(text))
        
        # Auto-resize columns
        self.results_table.resizeColumnsToContents()
        
        # Update summary text
        summary = f"Statistical Analysis Summary\n"
        summary += f"Analyzed {len(columns)} columns with {len(measures)} measures\n"
        summary += f"Total data points per column: {list(results.values())[0]['Count']}\n"
        self.summary_text.setText(summary)
            
    def run_regression_analysis(self):
        """Run regression analysis and generate prediction data."""
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
            x_data = data[x_col].dropna()
            y_data = data[y_col].dropna()
            
            # Align data (remove NaN pairs)
            valid_mask = ~(pd.isna(data[x_col]) | pd.isna(data[y_col]))
            x_clean = data.loc[valid_mask, x_col].values
            y_clean = data.loc[valid_mask, y_col].values
            
            if len(x_clean) < 2:
                QMessageBox.warning(self, "Warning", "Insufficient data points for regression.")
                return
                
            self.progress_bar.setValue(50)
            
            # Perform linear regression
            X = x_clean.reshape(-1, 1)
            model = LinearRegression()
            model.fit(X, y_clean)
            
            # Generate predictions
            x_range = np.linspace(x_clean.min(), x_clean.max(), 100)
            y_pred = model.predict(x_range.reshape(-1, 1))
            
            # Calculate metrics
            y_pred_original = model.predict(X)
            r2 = r2_score(y_clean, y_pred_original)
            rmse = np.sqrt(mean_squared_error(y_clean, y_pred_original))
            
            self.progress_bar.setValue(75)
            
            # Generate prediction dataset if requested
            if self.generate_predictions_check.isChecked():
                prediction_data = pd.DataFrame({
                    f'{x_col}_predicted': x_range,
                    f'{y_col}_predicted': y_pred,
                    'residuals': np.nan,  # Placeholder
                    'confidence_interval_lower': np.nan,  # Placeholder  
                    'confidence_interval_upper': np.nan   # Placeholder
                })
                
                # Store generated data
                dataset_name = f"Regression_{x_col}_vs_{y_col}"
                self.generated_datasets[dataset_name] = prediction_data
                
                # Update generated data list
                self.update_generated_data_list()
                
                # Emit signal for main application
                self.data_created.emit(dataset_name, prediction_data)
                
            # Visualize regression
            self.visualize_regression_results(x_clean, y_clean, x_range, y_pred, x_col, y_col, r2, rmse, model)
            
            self.progress_bar.setValue(100)
            self.status_label.setText(f"Regression completed: R² = {r2:.4f}, RMSE = {rmse:.4f}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Regression analysis failed: {str(e)}")
            self.status_label.setText("Regression analysis failed")
        finally:
            self.progress_bar.setVisible(False)
            
    def visualize_regression_results(self, x_data, y_data, x_pred, y_pred, x_col, y_col, r2, rmse, model):
        """Visualize regression results."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Scatter plot of original data
        ax.scatter(x_data, y_data, alpha=0.6, color='blue', label='Data Points')
        
        # Regression line
        ax.plot(x_pred, y_pred, color='red', linewidth=2, label=f'Linear Fit (R² = {r2:.3f})')
        
        # Labels and title
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f'Linear Regression: {y_col} vs {x_col}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add equation text
        slope = model.coef_[0]
        intercept = model.intercept_
        equation = f'y = {slope:.4f}x + {intercept:.4f}'
        ax.text(0.05, 0.95, equation, transform=ax.transAxes, 
                bbox=dict(boxstyle="round", facecolor='wheat'), verticalalignment='top')
        
        self.figure.tight_layout()
        self.canvas.draw()
        
        # Switch to visualization tab
        self.results_tabs.setCurrentIndex(1)
        
    def run_transformation(self):
        """Run data transformation and generate transformed data."""
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
            
            self.progress_bar.setValue(25)
            
            # Create copy of data for transformation
            transformed_data = data.copy()
            
            # Apply transformation based on type
            for col in selected_columns:
                if col not in data.columns:
                    continue
                    
                col_data = data[col].dropna()
                if len(col_data) == 0:
                    continue
                    
                try:
                    if transformation == "Logarithmic (log)":
                        # Only apply to positive values
                        mask = data[col] > 0
                        transformed_data.loc[mask, f"{col}_log"] = np.log(data.loc[mask, col])
                        
                    elif transformation == "Square Root (sqrt)":
                        # Only apply to non-negative values
                        mask = data[col] >= 0
                        transformed_data.loc[mask, f"{col}_sqrt"] = np.sqrt(data.loc[mask, col])
                        
                    elif transformation == "Power Transform":
                        power = self.power_spin.value()
                        transformed_data[f"{col}_power{power}"] = np.power(data[col], power)
                        
                    elif transformation == "Z-Score Standardization":
                        mean_val = col_data.mean()
                        std_val = col_data.std()
                        if std_val > 0:
                            transformed_data[f"{col}_zscore"] = (data[col] - mean_val) / std_val
                            
                    elif transformation == "Min-Max Normalization":
                        min_val = col_data.min()
                        max_val = col_data.max()
                        if max_val > min_val:
                            transformed_data[f"{col}_normalized"] = (data[col] - min_val) / (max_val - min_val)
                            
                    elif transformation == "Differencing":
                        transformed_data[f"{col}_diff"] = data[col].diff()
                        
                except Exception as e:
                    print(f"Error transforming column {col}: {e}")
                    continue
            
            self.progress_bar.setValue(75)
            
            # Store generated data
            dataset_name = f"Transform_{transformation.split('(')[0].strip()}_{len(selected_columns)}cols"
            self.generated_datasets[dataset_name] = transformed_data
            
            # Update generated data list
            self.update_generated_data_list()
            
            # Emit signal for main application
            self.data_created.emit(dataset_name, transformed_data)
            
            self.progress_bar.setValue(100)
            self.status_label.setText(f"Transformation completed: {transformation}")
            
            # Show preview of transformed data
            self.show_data_preview(transformed_data)
            
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
        
        # Switch to generated data tab
        self.results_tabs.setCurrentIndex(2)
        
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
            self.show_data_preview(dataframe)
            
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
