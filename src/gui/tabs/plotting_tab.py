"""
Advanced Plotting Tab

Professional plotting interface with matplotlib integration, scientific features,
customization options, and high-performance rendering.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import ScalarFormatter, FuncFormatter, MultipleLocator
import seaborn as sns

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QComboBox, QLineEdit, QPushButton, QCheckBox, QSpinBox,
    QDoubleSpinBox, QLabel, QSplitter, QTabWidget, QColorDialog,
    QFileDialog, QMessageBox, QSlider, QButtonGroup, QRadioButton,
    QScrollArea, QFrame, QTextEdit, QSpacerItem, QSizePolicy, QApplication,
    QDialog
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor, QFont, QPixmap, QClipboard


class PlottingTab(QWidget):
    """Advanced plotting interface with real-time preview and scientific features."""
    
    def __init__(self, data_manager):
        """Initialize the plotting tab."""
        super().__init__()
        self.data_manager = data_manager
        self.current_plot_data = None
        
        # Store subplot configurations from advanced dialog
        self.subplot_configs_data = []
        
        # Internal settings storage - persists across window resizes and plot updates
        self.internal_settings = {
            'figure_size': (10, 10),  # Default figure size (width, height)
            'dpi': 100,
            'title': '',
            'xlabel': '',
            'ylabel': '',
            'fontsize': 12,
            'axis_fontsize': 10,
            'tick_fontsize': 8,
            'grid': True,
            'legend': True,
            'alpha': 0.8,
            'color_palette': 'Default',
            'plot_style': 'default',
            'line_settings': {
                'linewidth': 2.0,
                'linestyle': '-',
                'marker': 'None',
                'markersize': 6
            },
            'scatter_settings': {
                'marker': 'o',
                'markersize': 6,
                'size_scale': 1.0,
                'edge_width': 0.8
            },
            'bar_settings': {
                'bar_width': 0.8,
                'edge_width': 1.0,
                'orientation': 'Vertical'
            },
            'hist_settings': {
                'bins': 20,
                'bin_method': 'auto',
                'density': False,
                'cumulative': False
            },
            'axes_settings': {
                'logx': False,
                'logy': False,
                'scientific': False,
                'aspect': 'auto'
            },
            'multi_settings': {
                'grid_rows': 2,
                'grid_cols': 2,
                'hspace': 0.3,
                'wspace': 0.3,
                'individual_styling': False,
                'subplot_settings': []
            }
        }
        
        # Scientific styling options
        self.plot_styles = {
            'default': 'default',
            'scientific': 'seaborn-v0_8-whitegrid',
            'publication': 'seaborn-v0_8-white',
            'dark': 'dark_background',
            'minimal': 'bmh'
        }
        
        # Color palettes
        self.color_palettes = {
            'Default': 'tab10',
            'Scientific': 'Set1',
            'Colorblind': 'Set2',  # Set2 is colorblind-friendly
            'Viridis': 'viridis',
            'Plasma': 'plasma',
            'Cool': 'cool',
            'Warm': 'Reds',
            'Custom': 'custom'
        }
        
        self.setup_ui()
        self.setEnabled(False)  # Disabled until data is loaded
        
        # Performance: Update timer for real-time preview
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_plot_delayed)
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        
        # Create main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Controls
        controls_widget = self.create_controls_panel()
        controls_widget.setMaximumWidth(400)
        controls_widget.setMinimumWidth(350)
        
        # Right panel - Plot area
        plot_widget = self.create_plot_panel()
        
        splitter.addWidget(controls_widget)
        splitter.addWidget(plot_widget)
        splitter.setSizes([350, 1000])  # 25% controls, 75% plot
        
        layout.addWidget(splitter)
        
        # Initialize UI controls with internal settings
        self.sync_ui_to_internal_settings()
        
    def create_controls_panel(self):
        """Create the left control panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Scroll area for controls
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Data Selection Group
        data_group = self.create_data_selection_group()
        scroll_layout.addWidget(data_group)
        
        # Plot Type Group
        type_group = self.create_plot_type_group()
        scroll_layout.addWidget(type_group)
        
        # Styling Group
        style_group = self.create_styling_group()
        scroll_layout.addWidget(style_group)
        
        # Customization Group
        custom_group = self.create_customization_group()
        scroll_layout.addWidget(custom_group)
        
        # Scientific Features Group
        scientific_group = self.create_scientific_group()
        scroll_layout.addWidget(scientific_group)
        
        # Export Group
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
        """Create data selection controls."""
        group = QGroupBox("📊 Data Selection")
        layout = QGridLayout(group)
        
        # X-axis column
        layout.addWidget(QLabel("X-axis:"), 0, 0)
        self.x_combo = QComboBox()
        self.x_combo.currentTextChanged.connect(self.schedule_update)
        layout.addWidget(self.x_combo, 0, 1)
        
        # Y-axis column
        layout.addWidget(QLabel("Y-axis:"), 1, 0)
        self.y_combo = QComboBox()
        self.y_combo.currentTextChanged.connect(self.schedule_update)
        layout.addWidget(self.y_combo, 1, 1)
        
        # Color/Group column (optional)
        layout.addWidget(QLabel("Color by:"), 2, 0)
        self.color_combo = QComboBox()
        self.color_combo.addItem("None")
        self.color_combo.currentTextChanged.connect(self.schedule_update)
        layout.addWidget(self.color_combo, 2, 1)
        
        # Size column (for scatter plots)
        layout.addWidget(QLabel("Size by:"), 3, 0)
        self.size_combo = QComboBox()
        self.size_combo.addItem("None")
        self.size_combo.currentTextChanged.connect(self.schedule_update)
        layout.addWidget(self.size_combo, 3, 1)
        
        return group
        
    def create_plot_type_group(self):
        """Create plot type selection controls."""
        group = QGroupBox("📈 Plot Type")
        layout = QVBoxLayout(group)
        
        # Plot type dropdown
        layout.addWidget(QLabel("Plot Type:"))
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems([
            "📈 Line Plot",
            "⚫ Scatter Plot", 
            "📊 Bar Chart",
            "📏 Histogram",
            "📦 Box Plot",
            "🎻 Violin Plot",
            "🔥 Heatmap",
            "🔗 Pair Plot",
            "🎯 Multi-Plot Grid"
        ])
        self.plot_type_combo.currentTextChanged.connect(self.on_plot_type_changed)
        layout.addWidget(self.plot_type_combo)
        
        # Customization button (initially hidden - only for multi-plot)
        self.customize_button = QPushButton("⚙️ Advanced Grid Setup")
        self.customize_button.clicked.connect(self.open_customization_dialog)
        self.customize_button.hide()  # Initially hidden
        layout.addWidget(self.customize_button)
        
        # Multi-plot configuration (initially hidden)
        self.multi_plot_config = self.create_multi_plot_config()
        layout.addWidget(self.multi_plot_config)
        self.multi_plot_config.hide()
            
        return group
    
    def get_plot_type_from_combo(self):
        """Get the plot type key from combo box selection."""
        plot_type_map = {
            "📈 Line Plot": "line",
            "⚫ Scatter Plot": "scatter", 
            "📊 Bar Chart": "bar",
            "📏 Histogram": "hist",
            "📦 Box Plot": "box",
            "🎻 Violin Plot": "violin",
            "🔥 Heatmap": "heatmap",
            "🔗 Pair Plot": "pair",
            "🎯 Multi-Plot Grid": "multi"
        }
        return plot_type_map.get(self.plot_type_combo.currentText(), "line")
    
    def on_plot_type_changed(self):
        """Handle plot type change to show/hide relevant controls."""
        plot_type = self.get_plot_type_from_combo()
        
        # Show/hide multi-plot configuration and customization button
        if plot_type == "multi":
            self.multi_plot_config.show()
            self.customize_button.show()
        else:
            self.multi_plot_config.hide()
            self.customize_button.hide()
        
        # Update styling options based on plot type
        self.update_styling_options(plot_type)
        self.schedule_update()
    
    def open_customization_dialog(self):
        """Open the advanced customization dialog."""
        plot_type = self.get_plot_type_from_combo()
        dialog = PlotCustomizationDialog(self, plot_type)
        if dialog.exec() == 1:  # QDialog.Accepted = 1
            # Apply the customization settings
            self.apply_customization_settings(dialog.get_settings())
            self.schedule_update()
    
    def create_multi_plot_config(self):
        """Create multi-plot grid configuration."""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        # Grid size
        layout.addWidget(QLabel("Grid Size:"), 0, 0)
        self.grid_rows_spin = QSpinBox()
        self.grid_rows_spin.setRange(1, 5)
        self.grid_rows_spin.setValue(2)
        self.grid_rows_spin.valueChanged.connect(self.schedule_update)
        layout.addWidget(self.grid_rows_spin, 0, 1)
        
        layout.addWidget(QLabel("×"), 0, 2)
        self.grid_cols_spin = QSpinBox()
        self.grid_cols_spin.setRange(1, 5)
        self.grid_cols_spin.setValue(2)
        self.grid_cols_spin.valueChanged.connect(self.schedule_update)
        layout.addWidget(self.grid_cols_spin, 0, 3)
        
        # Note about advanced configuration
        note_label = QLabel("ℹ️ Use 'Advanced Grid Setup' button for detailed configuration")
        note_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(note_label, 1, 0, 1, 4)
        
        return widget
    
    def update_multi_plot_grid(self):
        """Update the multi-plot grid configuration - simplified for basic grid size only."""
        # This method is now simplified since detailed configuration is handled in the popup dialog
        # Just trigger a plot update when grid size changes
        self.schedule_update()
    
    def update_styling_options(self, plot_type):
        """Update styling options based on selected plot type."""
        # Hide all plot-specific controls first
        self.linewidth_label.hide()
        self.linewidth_spin.hide()
        self.markersize_label.hide()
        self.markersize_spin.hide()
        self.marker_label.hide()
        self.marker_combo.hide()
        self.linestyle_label.hide()
        self.linestyle_combo.hide()
        self.bins_label.hide()
        self.bins_spin.hide()
        self.bar_width_label.hide()
        self.bar_width_spin.hide()
        
        # Alpha (transparency) is always available
        self.alpha_slider.setEnabled(True)
        
        # Show relevant controls for each plot type
        if plot_type == "line":
            self.linewidth_label.show()
            self.linewidth_spin.show()
            self.markersize_label.show()
            self.markersize_spin.show()
            self.marker_label.show()
            self.marker_combo.show()
            self.linestyle_label.show()
            self.linestyle_combo.show()
        elif plot_type == "scatter":
            self.markersize_label.show()
            self.markersize_spin.show()
            self.marker_label.show()
            self.marker_combo.show()
        elif plot_type == "bar":
            self.bar_width_label.show()
            self.bar_width_spin.show()
        elif plot_type == "hist":
            self.bins_label.show()
            self.bins_spin.show()
        elif plot_type in ["box", "violin"]:
            self.linewidth_label.show()
            self.linewidth_spin.show()
        elif plot_type in ["heatmap", "pair"]:
            self.alpha_slider.setEnabled(False)
        elif plot_type == "multi":
            # For multi-plot, show all options as they may be needed
            self.linewidth_label.show()
            self.linewidth_spin.show()
            self.markersize_label.show()
            self.markersize_spin.show()
            self.marker_label.show()
            self.marker_combo.show()
            self.linestyle_label.show()
            self.linestyle_combo.show()
            self.bins_label.show()
            self.bins_spin.show()
            self.bar_width_label.show()
            self.bar_width_spin.show()
    
    def create_styling_group(self):
        """Create styling controls."""
        group = QGroupBox("🎨 Styling")
        layout = QGridLayout(group)
        
        # Style preset
        layout.addWidget(QLabel("Style:"), 0, 0)
        self.style_combo = QComboBox()
        self.style_combo.addItems(list(self.plot_styles.keys()))
        self.style_combo.currentTextChanged.connect(self.schedule_update)
        layout.addWidget(self.style_combo, 0, 1)
        
        # Color palette
        layout.addWidget(QLabel("Colors:"), 1, 0)
        self.palette_combo = QComboBox()
        self.palette_combo.addItems(list(self.color_palettes.keys()))
        self.palette_combo.currentTextChanged.connect(self.schedule_update)
        layout.addWidget(self.palette_combo, 1, 1)
        
        # Custom color button
        self.color_button = QPushButton("🎨 Custom")
        self.color_button.clicked.connect(self.choose_custom_color)
        layout.addWidget(self.color_button, 2, 0, 1, 2)
        
        # Line/marker settings with stored label references
        self.linewidth_label = QLabel("Line Width:")
        layout.addWidget(self.linewidth_label, 3, 0)
        self.linewidth_spin = QDoubleSpinBox()
        self.linewidth_spin.setRange(0.5, 10.0)
        self.linewidth_spin.setValue(2.0)
        self.linewidth_spin.setSingleStep(0.5)
        self.linewidth_spin.valueChanged.connect(self.schedule_update)
        layout.addWidget(self.linewidth_spin, 3, 1)
        
        self.markersize_label = QLabel("Marker Size:")
        layout.addWidget(self.markersize_label, 4, 0)
        self.markersize_spin = QSpinBox()
        self.markersize_spin.setRange(1, 20)
        self.markersize_spin.setValue(6)
        self.markersize_spin.valueChanged.connect(self.schedule_update)
        layout.addWidget(self.markersize_spin, 4, 1)
        
        # Marker style (for line and scatter plots)
        
        self.marker_label = QLabel("Marker Style:")
        layout.addWidget(self.marker_label, 5, 0)
        self.marker_combo = QComboBox()
        self.marker_combo.addItems([
            "None", "o", "s", "^", "v", "<", ">", "D", "p", "*", "+", "x"
        ])
        self.marker_combo.currentTextChanged.connect(self.schedule_update)
        layout.addWidget(self.marker_combo, 5, 1)
        
        # Line style (for line plots)
        self.linestyle_label = QLabel("Line Style:")
        layout.addWidget(self.linestyle_label, 6, 0)
        self.linestyle_combo = QComboBox()
        self.linestyle_combo.addItems([
            "-", "--", "-.", ":", "None"
        ])
        self.linestyle_combo.currentTextChanged.connect(self.schedule_update)
        layout.addWidget(self.linestyle_combo, 6, 1)
        
        # Histogram bins (for histograms)
        self.bins_label = QLabel("Bins:")
        layout.addWidget(self.bins_label, 7, 0)
        self.bins_spin = QSpinBox()
        self.bins_spin.setRange(5, 100)
        self.bins_spin.setValue(20)
        self.bins_spin.valueChanged.connect(self.schedule_update)
        layout.addWidget(self.bins_spin, 7, 1)
        
        # Bar width (for bar plots)
        self.bar_width_label = QLabel("Bar Width:")
        layout.addWidget(self.bar_width_label, 8, 0)
        self.bar_width_spin = QDoubleSpinBox()
        self.bar_width_spin.setRange(0.1, 2.0)
        self.bar_width_spin.setValue(0.8)
        self.bar_width_spin.setSingleStep(0.1)
        self.bar_width_spin.valueChanged.connect(self.schedule_update)
        layout.addWidget(self.bar_width_spin, 8, 1)        # Alpha (transparency)
        layout.addWidget(QLabel("Transparency:"), 9, 0)
        self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setRange(10, 100)
        self.alpha_slider.setValue(80)
        self.alpha_slider.valueChanged.connect(self.schedule_update)
        layout.addWidget(self.alpha_slider, 9, 1)
        
        return group
        
    def create_customization_group(self):
        """Create plot customization controls."""
        group = QGroupBox("⚙️ Customization")
        layout = QGridLayout(group)
        
        # Title
        layout.addWidget(QLabel("Title:"), 0, 0)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter plot title...")
        self.title_edit.textChanged.connect(self.schedule_update)
        layout.addWidget(self.title_edit, 0, 1)
        
        # X-axis label
        layout.addWidget(QLabel("X Label:"), 1, 0)
        self.xlabel_edit = QLineEdit()
        self.xlabel_edit.textChanged.connect(self.schedule_update)
        layout.addWidget(self.xlabel_edit, 1, 1)
        
        # Y-axis label
        layout.addWidget(QLabel("Y Label:"), 2, 0)
        self.ylabel_edit = QLineEdit()
        self.ylabel_edit.textChanged.connect(self.schedule_update)
        layout.addWidget(self.ylabel_edit, 2, 1)
        
        # Font size
        layout.addWidget(QLabel("Font Size:"), 3, 0)
        self.fontsize_spin = QSpinBox()
        self.fontsize_spin.setRange(8, 24)
        self.fontsize_spin.setValue(12)
        self.fontsize_spin.valueChanged.connect(self.schedule_update)
        layout.addWidget(self.fontsize_spin, 3, 1)
        
        # Checkboxes for various options
        self.grid_check = QCheckBox("Show Grid")
        self.grid_check.setChecked(True)
        self.grid_check.toggled.connect(self.schedule_update)
        layout.addWidget(self.grid_check, 4, 0, 1, 2)
        
        self.legend_check = QCheckBox("Show Legend")
        self.legend_check.setChecked(True)
        self.legend_check.toggled.connect(self.schedule_update)
        layout.addWidget(self.legend_check, 5, 0, 1, 2)
        
        self.tight_layout_check = QCheckBox("Tight Layout")
        self.tight_layout_check.setChecked(True)
        self.tight_layout_check.toggled.connect(self.schedule_update)
        layout.addWidget(self.tight_layout_check, 6, 0, 1, 2)
        
        return group
        
    def create_scientific_group(self):
        """Create scientific features controls."""
        group = QGroupBox("🔬 Scientific Features")
        layout = QGridLayout(group)
        
        # Scientific notation
        self.scientific_check = QCheckBox("Scientific Notation")
        self.scientific_check.toggled.connect(self.schedule_update)
        layout.addWidget(self.scientific_check, 0, 0, 1, 2)
        
        # Log scale options
        self.logx_check = QCheckBox("Log Scale X")
        self.logx_check.toggled.connect(self.schedule_update)
        layout.addWidget(self.logx_check, 1, 0)
        
        self.logy_check = QCheckBox("Log Scale Y")
        self.logy_check.toggled.connect(self.schedule_update)
        layout.addWidget(self.logy_check, 1, 1)
        
        # Error bars (if available)
        self.errorbar_check = QCheckBox("Error Bars")
        self.errorbar_check.toggled.connect(self.schedule_update)
        layout.addWidget(self.errorbar_check, 2, 0, 1, 2)
        
        # Aspect ratio
        layout.addWidget(QLabel("Aspect:"), 3, 0)
        self.aspect_combo = QComboBox()
        self.aspect_combo.addItems(["auto", "equal", "1:1", "4:3", "16:9"])
        self.aspect_combo.currentTextChanged.connect(self.schedule_update)
        layout.addWidget(self.aspect_combo, 3, 1)
        
        # DPI for high-quality output
        layout.addWidget(QLabel("DPI:"), 4, 0)
        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(72, 600)
        self.dpi_spin.setValue(300)
        self.dpi_spin.valueChanged.connect(self.schedule_update)
        layout.addWidget(self.dpi_spin, 4, 1)
        
        # Figure size controls
        layout.addWidget(QLabel("Figure Width:"), 5, 0)
        self.figure_width_spin = QDoubleSpinBox()
        self.figure_width_spin.setRange(3.0, 20.0)
        self.figure_width_spin.setValue(10.0)
        self.figure_width_spin.setSingleStep(0.5)
        self.figure_width_spin.valueChanged.connect(self.schedule_update)
        layout.addWidget(self.figure_width_spin, 5, 1)
        
        layout.addWidget(QLabel("Figure Height:"), 6, 0)
        self.figure_height_spin = QDoubleSpinBox()
        self.figure_height_spin.setRange(2.0, 15.0)
        self.figure_height_spin.setValue(6.0)
        self.figure_height_spin.setSingleStep(0.5)
        self.figure_height_spin.valueChanged.connect(self.schedule_update)
        layout.addWidget(self.figure_height_spin, 6, 1)
        
        return group
        
    def create_export_group(self):
        """Create export controls."""
        group = QGroupBox("💾 Export")
        layout = QVBoxLayout(group)
        
        # Export buttons
        export_buttons = [
            ("📄 Export PDF", "pdf"),
            ("🖼️ Export PNG", "png"),
            ("📊 Export SVG", "svg"),
            ("📈 Export JPG", "jpg"),
            ("📋 Copy to Clipboard", "clipboard")
        ]
        
        for label, format_type in export_buttons:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, fmt=format_type: self.export_plot(fmt))
            layout.addWidget(btn)
            
        # LaTeX export button
        #latex_btn = QPushButton("📝 Export LaTeX")
        #latex_btn.clicked.connect(self.export_latex)
        #layout.addWidget(latex_btn)
        
        return group
        
    def create_plot_panel(self):
        """Create the plot display panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Set a simple background pattern to show plot boundaries
        widget.setStyleSheet("""
            QWidget {
                background-color: #555555;
                background-image: 
                    repeating-linear-gradient(45deg, 
                        transparent, 
                        transparent 10px, 
                        #e8e8e8 10px, 
                        #e8e8e8 20px);
            }
        """)
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(10, 10), dpi=100, facecolor="#555555")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(widget)
        #f8f8f8
        # Set canvas background to show plot area clearly
        self.canvas.setStyleSheet("""
            FigureCanvas {
                background-color: #f8f8f8;
                border: 2px solid #cccccc;
                border-radius: 4px;
                margin: 5px;
            }
        """)
        
        # Add navigation toolbar
        from matplotlib.backends.backend_qt import NavigationToolbar2QT
        self.toolbar = NavigationToolbar2QT(self.canvas, widget)
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # Status label
        self.status_label = QLabel("Ready to plot...")
        self.status_label.setStyleSheet("color: #666; font-style: italic; background: transparent;")
        layout.addWidget(self.status_label)
        
        return widget
        
    def sync_ui_to_internal_settings(self):
        """Sync UI controls to internal settings - called when loading or resetting."""
        # General settings
        self.title_edit.setText(self.internal_settings['title'])
        self.xlabel_edit.setText(self.internal_settings['xlabel'])
        self.ylabel_edit.setText(self.internal_settings['ylabel'])
        self.fontsize_spin.setValue(self.internal_settings['fontsize'])
        self.grid_check.setChecked(self.internal_settings['grid'])
        self.legend_check.setChecked(self.internal_settings['legend'])
        self.alpha_slider.setValue(int(self.internal_settings['alpha'] * 100))
        self.palette_combo.setCurrentText(self.internal_settings['color_palette'])
        self.style_combo.setCurrentText(self.internal_settings['plot_style'])
        
        # Line settings
        line_settings = self.internal_settings['line_settings']
        self.linewidth_spin.setValue(line_settings['linewidth'])
        self.linestyle_combo.setCurrentText(line_settings['linestyle'])
        self.marker_combo.setCurrentText(line_settings['marker'])
        self.markersize_spin.setValue(line_settings['markersize'])
        
        # Scatter settings
        scatter_settings = self.internal_settings['scatter_settings']
        # markersize_spin is shared with line settings
        
        # Bar settings
        bar_settings = self.internal_settings['bar_settings']
        self.bar_width_spin.setValue(bar_settings['bar_width'])
        
        # Histogram settings
        hist_settings = self.internal_settings['hist_settings']
        self.bins_spin.setValue(hist_settings['bins'])
        
        # Axes settings
        axes_settings = self.internal_settings['axes_settings']
        self.logx_check.setChecked(axes_settings['logx'])
        self.logy_check.setChecked(axes_settings['logy'])
        self.scientific_check.setChecked(axes_settings['scientific'])
        self.aspect_combo.setCurrentText(axes_settings['aspect'])
        
        # Multi-plot settings
        multi_settings = self.internal_settings['multi_settings']
        self.grid_rows_spin.setValue(multi_settings['grid_rows'])
        self.grid_cols_spin.setValue(multi_settings['grid_cols'])
        
        # Figure settings
        figure_size = self.internal_settings['figure_size']
        self.figure_width_spin.setValue(figure_size[0])
        self.figure_height_spin.setValue(figure_size[1])
        self.dpi_spin.setValue(self.internal_settings['dpi'])
        
    def update_internal_settings_from_ui(self):
        """Update internal settings from current UI state - called when UI changes."""
        # General settings
        self.internal_settings['title'] = self.title_edit.text()
        self.internal_settings['xlabel'] = self.xlabel_edit.text()
        self.internal_settings['ylabel'] = self.ylabel_edit.text()
        self.internal_settings['fontsize'] = self.fontsize_spin.value()
        self.internal_settings['grid'] = self.grid_check.isChecked()
        self.internal_settings['legend'] = self.legend_check.isChecked()
        self.internal_settings['alpha'] = self.alpha_slider.value() / 100.0
        self.internal_settings['color_palette'] = self.palette_combo.currentText()
        self.internal_settings['plot_style'] = self.style_combo.currentText()
        
        # Line settings
        self.internal_settings['line_settings']['linewidth'] = self.linewidth_spin.value()
        self.internal_settings['line_settings']['linestyle'] = self.linestyle_combo.currentText()
        self.internal_settings['line_settings']['marker'] = self.marker_combo.currentText()
        self.internal_settings['line_settings']['markersize'] = self.markersize_spin.value()
        
        # Scatter settings  
        self.internal_settings['scatter_settings']['marker'] = self.marker_combo.currentText()
        self.internal_settings['scatter_settings']['markersize'] = self.markersize_spin.value()
        
        # Bar settings
        self.internal_settings['bar_settings']['bar_width'] = self.bar_width_spin.value()
        
        # Histogram settings
        self.internal_settings['hist_settings']['bins'] = self.bins_spin.value()
        
        # Axes settings
        self.internal_settings['axes_settings']['logx'] = self.logx_check.isChecked()
        self.internal_settings['axes_settings']['logy'] = self.logy_check.isChecked()
        self.internal_settings['axes_settings']['scientific'] = self.scientific_check.isChecked()
        self.internal_settings['axes_settings']['aspect'] = self.aspect_combo.currentText()
        
        # Multi-plot settings
        self.internal_settings['multi_settings']['grid_rows'] = self.grid_rows_spin.value()
        self.internal_settings['multi_settings']['grid_cols'] = self.grid_cols_spin.value()
        
        # Figure settings
        self.internal_settings['figure_size'] = (self.figure_width_spin.value(), self.figure_height_spin.value())
        self.internal_settings['dpi'] = self.dpi_spin.value()
        
    def apply_figure_settings(self):
        """Apply figure-level settings at the beginning of plotting."""
        # Set figure size and DPI from internal settings
        width, height = self.internal_settings['figure_size']
        dpi = self.internal_settings['dpi']
        
        # Clear and reconfigure the figure with saved settings
        self.figure.clear()
        self.figure.set_size_inches(width, height)
        self.figure.set_dpi(dpi)
        
        # Set figure background to white for consistency
        self.figure.patch.set_facecolor("white")
        self.figure.patch.set_edgecolor("lightgray")
        self.figure.patch.set_linewidth(1)
        
        # Apply the selected plot style
        plot_style = self.internal_settings['plot_style']
        if plot_style in self.plot_styles:
            plt.style.use(self.plot_styles[plot_style])
        
    def get_current_settings(self):
        """Get current settings as a dictionary (for saving/loading)."""
        # Update internal settings from UI first
        self.update_internal_settings_from_ui()
        return self.internal_settings.copy()
    
    def apply_settings(self, settings):
        """Apply settings dictionary to internal storage and UI."""
        # Update internal settings
        self.internal_settings.update(settings)
        
        # Sync UI to match internal settings
        self.sync_ui_to_internal_settings()
        
        # Trigger plot update
        self.schedule_update()
        
    def update_column_lists(self):
        """Update column selection dropdowns when new data is loaded."""
        if not self.data_manager.has_data():
            self.setEnabled(False)
            return
            
        self.setEnabled(True)
        columns = self.data_manager.get_analysis_columns()  # Exclude sample_id
        numeric_columns = self.data_manager.get_analysis_numeric_columns()  # Exclude sample_id
        
        # Clear and populate X/Y combo boxes with numeric columns
        self.x_combo.clear()
        self.y_combo.clear()
        self.x_combo.addItems(numeric_columns)
        self.y_combo.addItems(numeric_columns)
        
        # Color and size can use any column
        self.color_combo.clear()
        self.size_combo.clear()
        self.color_combo.addItem("None")
        self.size_combo.addItem("None")
        self.color_combo.addItems(columns)
        self.size_combo.addItems(numeric_columns)
        
        # Auto-populate labels
        if len(numeric_columns) >= 2:
            self.xlabel_edit.setText(numeric_columns[0])
            self.ylabel_edit.setText(numeric_columns[1])
            
        self.schedule_update()
        
    def schedule_update(self):
        """Schedule a plot update with a small delay for performance."""
        if self.data_manager.has_data():
            # Update internal settings from UI before plotting
            self.update_internal_settings_from_ui()
            self.update_timer.start(100)  # 100ms delay
            
    def update_plot_delayed(self):
        """Delayed plot update for better performance."""
        self.update_plot()
        
    def update_plot(self):
        """Update the plot based on current settings."""
        if not self.data_manager.has_data():
            return
            
        try:
            self.status_label.setText("Updating plot...")
            
            # Apply figure-level settings at the beginning (size, DPI, style)
            self.apply_figure_settings()
            
            # Get selected plot type
            plot_type = self.get_plot_type_from_combo()
                
            # Generate plot based on type
            if plot_type == "multi":
                self.create_multi_plot()
            else:
                # Create single subplot
                ax = self.figure.add_subplot(111)
                ax.set_facecolor('white')  # Ensure plot area is white
                
                if plot_type == "line":
                    self.create_line_plot(ax)
                elif plot_type == "scatter":
                    self.create_scatter_plot(ax)
                elif plot_type == "bar":
                    self.create_bar_plot(ax)
                elif plot_type == "hist":
                    self.create_histogram(ax)
                elif plot_type == "box":
                    self.create_box_plot(ax)
                elif plot_type == "violin":
                    self.create_violin_plot(ax)
                elif plot_type == "heatmap":
                    self.create_heatmap()
                elif plot_type == "pair":
                    self.create_pair_plot()
                    
                # Apply common formatting for single plots
                if plot_type not in ["heatmap", "pair"]:
                    self.apply_formatting(ax)
            
            # Refresh canvas
            self.canvas.draw()
            self.status_label.setText("Plot updated successfully")
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            print(f"Plot error: {e}")
            
    def create_line_plot(self, ax):
        """Create a line plot."""
        data = self.data_manager.get_data()
        x_col = self.x_combo.currentText()
        y_col = self.y_combo.currentText()
        color_col = self.color_combo.currentText()
        
        if not x_col or not y_col or x_col == y_col:
            return
        
        # Sort data by x-column for proper line connections
        data_sorted = data.sort_values(by=x_col)
        x_data = data_sorted[x_col]
        y_data = data_sorted[y_col]
        
        # Get styling parameters
        linewidth = self.linewidth_spin.value()
        alpha = self.alpha_slider.value() / 100.0
        marker = self.marker_combo.currentText() if self.marker_combo.currentText() != "None" else None
        linestyle = self.linestyle_combo.currentText() if self.linestyle_combo.currentText() != "None" else "-"
        
        if color_col and color_col != "None":
            # Group by color column and sort each group
            for group_name, group_data in data.groupby(color_col):
                group_sorted = group_data.sort_values(by=x_col)
                ax.plot(group_sorted[x_col], group_sorted[y_col], 
                       label=str(group_name), linewidth=linewidth, alpha=alpha,
                       marker=marker, linestyle=linestyle)
        else:
            # Single line
            color = self.get_current_color()
            ax.plot(x_data, y_data, color=color, linewidth=linewidth, alpha=alpha,
                   marker=marker, linestyle=linestyle)
            
        # Add markers if desired
        marker_style = getattr(self, 'marker_combo', None)
        if marker_style and hasattr(marker_style, 'currentText'):
            marker = marker_style.currentText()
            if marker != "None":
                # Re-plot with markers
                if color_col and color_col != "None":
                    for group_name, group_data in data.groupby(color_col):
                        group_sorted = group_data.sort_values(by=x_col)
                        ax.plot(group_sorted[x_col], group_sorted[y_col], 
                               marker=marker, linewidth=linewidth, alpha=alpha,
                               label=str(group_name))
                else:
                    color = self.get_current_color()
                    ax.plot(x_data, y_data, marker=marker, color=color, 
                           linewidth=linewidth, alpha=alpha)
            
    def create_scatter_plot(self, ax):
        """Create a scatter plot."""
        data = self.data_manager.get_data()
        x_col = self.x_combo.currentText()
        y_col = self.y_combo.currentText()
        color_col = self.color_combo.currentText()
        size_col = self.size_combo.currentText()
        
        if not x_col or not y_col:
            return
            
        x_data = data[x_col]
        y_data = data[y_col]
        
        # Get styling parameters
        base_size = self.markersize_spin.value() * 8  # Scale for scatter
        alpha = self.alpha_slider.value() / 100.0
        marker = self.marker_combo.currentText() if self.marker_combo.currentText() != "None" else "o"
        
        # Handle size mapping
        sizes = base_size
        if size_col and size_col != "None":
            size_data = data[size_col]
            sizes = (size_data - size_data.min()) / (size_data.max() - size_data.min()) * base_size * 2 + base_size
            
        # Handle color mapping
        if color_col and color_col != "None":
            if data[color_col].dtype in ['object', 'category']:
                # Categorical colors
                for group_name, group_data in data.groupby(color_col):
                    group_sizes = base_size
                    if size_col and size_col != "None":
                        group_size_data = group_data[size_col]
                        group_sizes = (group_size_data - group_size_data.min()) / (group_size_data.max() - group_size_data.min()) * base_size * 2 + base_size
                    ax.scatter(group_data[x_col], group_data[y_col], 
                             label=str(group_name), s=group_sizes, alpha=alpha, marker=marker)
            else:
                # Continuous colors
                scatter = ax.scatter(x_data, y_data, c=data[color_col], s=sizes, 
                                   alpha=alpha, cmap=self.get_current_colormap(), marker=marker)
                self.figure.colorbar(scatter, ax=ax, label=color_col)
        else:
            # Single color
            color = self.get_current_color()
            ax.scatter(x_data, y_data, color=color, s=sizes, alpha=alpha, marker=marker)
            
    def create_bar_plot(self, ax):
        """Create a bar plot."""
        data = self.data_manager.get_data()
        x_col = self.x_combo.currentText()
        y_col = self.y_combo.currentText()
        
        if not x_col or not y_col:
            return
            
        # For bar plots, aggregate data if needed
        if data[x_col].dtype in ['object', 'category']:
            plot_data = data.groupby(x_col, observed=False)[y_col].mean()
        else:
            # Bin numeric data
            plot_data = data.groupby(pd.cut(data[x_col], bins=20), observed=False)[y_col].mean()
            
        alpha = self.alpha_slider.value() / 100.0
        bar_width = self.bar_width_spin.value()
        color = self.get_current_color()
        
        ax.bar(range(len(plot_data)), plot_data.values, color=color, alpha=alpha, width=bar_width)
        ax.set_xticks(range(len(plot_data)))
        ax.set_xticklabels([str(x) for x in plot_data.index], rotation=45)
        
    def create_histogram(self, ax):
        """Create a histogram."""
        data = self.data_manager.get_data()
        x_col = self.x_combo.currentText()
        color_col = self.color_combo.currentText()
        
        if not x_col:
            return
            
        x_data = data[x_col]
        alpha = self.alpha_slider.value() / 100.0
        bins = self.bins_spin.value()
        
        if color_col and color_col != "None":
            # Multiple histograms
            for group_name, group_data in data.groupby(color_col):
                ax.hist(group_data[x_col], bins=bins, alpha=alpha, label=str(group_name))
        else:
            # Single histogram
            color = self.get_current_color()
            ax.hist(x_data, bins=bins, color=color, alpha=alpha)
            
    def create_box_plot(self, ax):
        """Create a box plot."""
        data = self.data_manager.get_data()
        x_col = self.x_combo.currentText()
        y_col = self.y_combo.currentText()
        
        if not y_col:
            return
            
        if x_col and data[x_col].dtype in ['object', 'category']:
            # Grouped box plot
            groups = [group[y_col].values for name, group in data.groupby(x_col)]
            labels = [str(name) for name, group in data.groupby(x_col)]
            ax.boxplot(groups, labels=labels)
        else:
            # Single box plot
            ax.boxplot(data[y_col].values)
            
    def create_violin_plot(self, ax):
        """Create a violin plot using seaborn."""
        data = self.data_manager.get_data()
        x_col = self.x_combo.currentText()
        y_col = self.y_combo.currentText()
        
        if not y_col:
            return
            
        if x_col and data[x_col].dtype in ['object', 'category']:
            sns.violinplot(data=data, x=x_col, y=y_col, ax=ax)
        else:
            sns.violinplot(y=data[y_col], ax=ax)
            
    def create_heatmap(self):
        """Create a correlation heatmap."""
        data = self.data_manager.get_data()
        numeric_data = data.select_dtypes(include=[np.number])
        
        if numeric_data.empty:
            return
            
        # Clear figure and create heatmap
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('white')  # Ensure plot area is white
        
        correlation_matrix = numeric_data.corr()
        sns.heatmap(correlation_matrix, annot=True, cmap=self.get_current_colormap(), 
                   center=0, ax=ax, cbar_kws={'label': 'Correlation'})
        ax.set_title("Correlation Heatmap")
        
    def create_pair_plot(self):
        """Create a pair plot of numeric columns."""
        data = self.data_manager.get_data()
        numeric_cols = self.data_manager.get_analysis_numeric_columns()  # Exclude sample_id
        
        if len(numeric_cols) < 2:
            return
            
        # Use up to 5 columns for performance
        cols_to_plot = numeric_cols[:5]
        plot_data = data[cols_to_plot]
        
        # Clear figure
        self.figure.clear()
        
        # Create pair plot manually (simplified version)
        n_cols = len(cols_to_plot)
        for i in range(n_cols):
            for j in range(n_cols):
                ax = self.figure.add_subplot(n_cols, n_cols, i * n_cols + j + 1)
                ax.set_facecolor('white')  # Ensure each subplot has white background
                if i == j:
                    # Diagonal: histogram
                    ax.hist(plot_data.iloc[:, i], bins=20, alpha=0.7)
                else:
                    # Off-diagonal: scatter
                    ax.scatter(plot_data.iloc[:, j], plot_data.iloc[:, i], alpha=0.6)
                    
                if i == n_cols - 1:
                    ax.set_xlabel(cols_to_plot[j])
                if j == 0:
                    ax.set_ylabel(cols_to_plot[i])
    
    def create_multi_plot(self):
        """Create multiple plots in a grid layout."""
        data = self.data_manager.get_data()
        rows = self.grid_rows_spin.value()
        cols = self.grid_cols_spin.value()
        
        # Get current X and Y columns from main selection (defaults)
        default_x_col = self.x_combo.currentText()
        default_y_col = self.y_combo.currentText()
        color_col = self.color_combo.currentText()
        
        if not default_x_col or not default_y_col:
            return
        
        # Clear the figure
        self.figure.clear()
        
        # Create basic multi-plot grid with same data
        # This is the default view - detailed configuration is done through the popup dialog
        for i in range(rows):
            for j in range(cols):
                subplot_num = i * cols + j + 1
                if subplot_num > rows * cols:
                    break
                    
                ax = self.figure.add_subplot(rows, cols, subplot_num)
                ax.set_facecolor('white')  # Ensure each subplot has white background
                
                # Get plot type from dialog configuration if available
                subplot_index = i * cols + j
                plot_type = "line"  # Default fallback
                x_col = default_x_col  # Default to main selection
                y_col = default_y_col  # Default to main selection
                custom_title = f"Plot {subplot_num}: {y_col} vs {x_col}"
                subplot_limits = None
                
                # Debug: Print what we're checking
                print(f"DEBUG: Creating subplot {subplot_index} at position ({i},{j})")
                print(f"DEBUG: hasattr subplot_configs_data: {hasattr(self, 'subplot_configs_data')}")
                
                # Check if we have advanced dialog configurations
                if hasattr(self, 'subplot_configs_data') and self.subplot_configs_data:
                    print(f"DEBUG: subplot_configs_data exists, length: {len(self.subplot_configs_data)}")
                    if subplot_index < len(self.subplot_configs_data):
                        try:
                            print(f"DEBUG: Reading config for subplot {subplot_index}")
                            config_data = self.subplot_configs_data[subplot_index]
                            
                            # Read plot type from the stored configuration
                            plot_type_text = config_data['plot_type']
                            plot_type = plot_type_text.lower()  # Convert "Line" to "line"
                            print(f"DEBUG: Plot type changed from 'line' to '{plot_type}' (from '{plot_type_text}')")
                            
                            # Read individual X/Y columns if specified
                            if 'x_column' in config_data and config_data['x_column']:
                                x_col = config_data['x_column']
                                print(f"DEBUG: Using custom X column: '{x_col}'")
                            else:
                                print(f"DEBUG: No custom X column found, using default: '{x_col}'")
                            
                            if 'y_column' in config_data and config_data['y_column']:
                                y_col = config_data['y_column']
                                print(f"DEBUG: Using custom Y column: '{y_col}'")
                            else:
                                print(f"DEBUG: No custom Y column found, using default: '{y_col}'")
                            
                            # Also apply title from stored configuration if available
                            dialog_title = config_data['title']
                            if dialog_title.strip():
                                custom_title = dialog_title
                                print(f"DEBUG: Custom title: '{custom_title}'")
                            else:
                                # Update default title with actual columns used
                                custom_title = f"Plot {subplot_num}: {y_col} vs {x_col}"
                                
                            # Apply axis limits if configured and individual styling is enabled
                            if config_data['individual_styling_enabled'] and config_data.get('axes_enabled', True):
                                try:
                                    xlim_min = config_data['xlim_min']
                                    xlim_max = config_data['xlim_max']
                                    ylim_min = config_data['ylim_min']
                                    ylim_max = config_data['ylim_max']
                                    
                                    # Store limits to apply after creating the plot
                                    subplot_limits = {
                                        'xlim': (xlim_min, xlim_max),
                                        'ylim': (ylim_min, ylim_max)
                                    }
                                    print(f"DEBUG: Axis limits set: X({xlim_min}, {xlim_max}), Y({ylim_min}, {ylim_max})")
                                except Exception as e:
                                    print(f"DEBUG: Error reading axis limits: {e}")
                                    subplot_limits = None
                            else:
                                print(f"DEBUG: Individual axes styling not enabled (individual_styling_enabled={config_data['individual_styling_enabled']}, axes_enabled={config_data.get('axes_enabled', True)})")
                        except Exception as e:
                            print(f"DEBUG: Error reading subplot config for {subplot_index}: {e}")
                            plot_type = "line"
                            x_col = default_x_col
                            y_col = default_y_col
                            custom_title = f"Plot {subplot_num}: {y_col} vs {x_col}"
                            subplot_limits = None
                    else:
                        print(f"DEBUG: No config available for subplot {subplot_index}")
                else:
                    print("DEBUG: No subplot_configs_data found - using defaults")
                
                print(f"DEBUG: Final plot_type for subplot {subplot_index}: '{plot_type}'")
                
                self.create_subplot_plot(ax, plot_type, data, x_col, y_col, color_col)
                
                # Apply basic formatting
                ax.set_title(custom_title, fontsize=10)
                ax.set_xlabel(x_col, fontsize=9)
                ax.set_ylabel(y_col, fontsize=9)
                
                # Apply custom limits if available
                if subplot_limits:
                    try:
                        ax.set_xlim(subplot_limits['xlim'])
                        ax.set_ylim(subplot_limits['ylim'])
                        print(f"DEBUG: Applied limits to subplot {subplot_index}")
                    except Exception as e:
                        print(f"DEBUG: Error setting subplot limits: {e}")
        
        # Adjust layout to prevent overlap
        self.figure.tight_layout()
    
    def create_subplot_plot(self, ax, plot_type, data, x_col, y_col, color_col):
        """Create a specific plot type for a subplot."""
        print(f"DEBUG: create_subplot_plot called with plot_type='{plot_type}', x_col='{x_col}', y_col='{y_col}'")
        
        # Validate that columns exist in data
        if x_col not in data.columns:
            print(f"ERROR: X column '{x_col}' not found in data. Available columns: {list(data.columns)}")
            ax.text(0.5, 0.5, f"Error: X column '{x_col}' not found", 
                   ha='center', va='center', transform=ax.transAxes)
            return
            
        if y_col not in data.columns:
            print(f"ERROR: Y column '{y_col}' not found in data. Available columns: {list(data.columns)}")
            ax.text(0.5, 0.5, f"Error: Y column '{y_col}' not found", 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        x_data = data[x_col]
        y_data = data[y_col]
        
        print(f"DEBUG: x_data shape: {x_data.shape}, y_data shape: {y_data.shape}")
        print(f"DEBUG: x_data range: {x_data.min()} to {x_data.max()}")
        print(f"DEBUG: y_data range: {y_data.min()} to {y_data.max()}")
        
        # Get styling parameters
        linewidth = self.linewidth_spin.value()
        markersize = self.markersize_spin.value()
        alpha = self.alpha_slider.value() / 100.0
        marker = self.marker_combo.currentText() if self.marker_combo.currentText() != "None" else "o"
        linestyle = self.linestyle_combo.currentText() if self.linestyle_combo.currentText() != "None" else "-"
        bins = self.bins_spin.value()
        bar_width = self.bar_width_spin.value()
        
        if plot_type == "line":
            # Sort data for proper line connections
            data_sorted = data.sort_values(by=x_col)
            if color_col and color_col != "None":
                for group_name, group_data in data.groupby(color_col):
                    group_sorted = group_data.sort_values(by=x_col)
                    ax.plot(group_sorted[x_col], group_sorted[y_col], 
                           label=str(group_name), linewidth=linewidth, alpha=alpha,
                           marker=marker, linestyle=linestyle)
                ax.legend(fontsize=8)
            else:
                data_sorted = data.sort_values(by=x_col)
                ax.plot(data_sorted[x_col], data_sorted[y_col], 
                       linewidth=linewidth, alpha=alpha, marker=marker, linestyle=linestyle)
                       
        elif plot_type == "scatter":
            if color_col and color_col != "None":
                scatter = ax.scatter(x_data, y_data, c=data[color_col], 
                                   s=markersize*5, alpha=alpha, cmap=self.get_current_colormap(), marker=marker)
                if len(data[color_col].unique()) <= 10:  # Only show colorbar for reasonable number of categories
                    plt.colorbar(scatter, ax=ax)
            else:
                ax.scatter(x_data, y_data, s=markersize*5, alpha=alpha, marker=marker)
                
        elif plot_type == "bar":
            if color_col and color_col != "None":
                # Group by color column and create grouped bar chart
                grouped = data.groupby(color_col, observed=False)[y_col].mean()
                ax.bar(range(len(grouped)), grouped.values, alpha=alpha, width=bar_width)
                ax.set_xticks(range(len(grouped)))
                ax.set_xticklabels(grouped.index, rotation=45)
            else:
                # Simple bar chart
                if data[x_col].dtype in ['object', 'category']:
                    grouped = data.groupby(x_col, observed=False)[y_col].mean()
                    ax.bar(range(len(grouped)), grouped.values, alpha=alpha, width=bar_width)
                    ax.set_xticks(range(len(grouped)))
                    ax.set_xticklabels(grouped.index, rotation=45)
                else:
                    ax.bar(x_data, y_data, alpha=alpha, width=bar_width)
                    
        elif plot_type == "hist":
            ax.hist(y_data, bins=bins, alpha=alpha)
            ax.set_xlabel(y_col)
            ax.set_ylabel("Frequency")
            
        elif plot_type == "box":
            if color_col and color_col != "None":
                # Box plot by category
                categories = data[color_col].unique()
                box_data = [data[data[color_col] == cat][y_col].dropna() for cat in categories]
                ax.boxplot(box_data, labels=categories)
                ax.set_xticklabels(categories, rotation=45)
            else:
                ax.boxplot([y_data.dropna()])
                ax.set_xticklabels([y_col])
                
        elif plot_type == "violin":
            if color_col and color_col != "None":
                # Violin plot by category
                import seaborn as sns
                sns.violinplot(data=data, x=color_col, y=y_col, ax=ax)
                ax.tick_params(axis='x', rotation=45)
            else:
                import seaborn as sns
                sns.violinplot(y=y_data, ax=ax)
                    
    def apply_formatting(self, ax):
        """Apply common formatting to the plot using internal settings."""
        # Title and labels from internal settings
        title = self.internal_settings['title']
        if title:
            ax.set_title(title, fontsize=self.internal_settings['fontsize'] + 2)
            
        xlabel = self.internal_settings['xlabel']
        if xlabel:
            axis_fontsize = self.internal_settings.get('axis_fontsize', self.internal_settings['fontsize'])
            ax.set_xlabel(xlabel, fontsize=axis_fontsize)
            
        ylabel = self.internal_settings['ylabel']
        if ylabel:
            axis_fontsize = self.internal_settings.get('axis_fontsize', self.internal_settings['fontsize'])
            ax.set_ylabel(ylabel, fontsize=axis_fontsize)
            
        # Apply tick label font size
        if 'tick_fontsize' in self.internal_settings:
            ax.tick_params(axis='both', which='major', labelsize=self.internal_settings['tick_fontsize'])
            
        # Grid
        if self.internal_settings['grid']:
            ax.grid(True, alpha=0.3)
            
        # Legend
        if self.internal_settings['legend'] and ax.get_legend_handles_labels()[0]:
            ax.legend(fontsize=self.internal_settings['fontsize'] - 1)
            
        # Scientific notation
        if self.internal_settings['axes_settings']['scientific']:
            ax.ticklabel_format(style='scientific', axis='both', scilimits=(0,0))
            
        # Log scales
        if self.internal_settings['axes_settings']['logx']:
            ax.set_xscale('log')
        if self.internal_settings['axes_settings']['logy']:
            ax.set_yscale('log')
            
        # Aspect ratio
        aspect = self.internal_settings['axes_settings']['aspect']
        if aspect != "auto":
            if aspect == "equal" or aspect == "1:1":
                ax.set_aspect('equal')
            elif aspect == "4:3":
                ax.set_aspect(4/3)
            elif aspect == "16:9":
                ax.set_aspect(16/9)
                
        # Tight layout
        if hasattr(self, 'tight_layout_check') and self.tight_layout_check.isChecked():
            self.figure.tight_layout()
            
    def get_current_color(self):
        """Get the current color setting from internal settings."""
        palette_name = self.internal_settings['color_palette']
        if palette_name == "Custom":
            return getattr(self, 'custom_color', '#1f77b4')
        else:
            # Return first color from the palette
            if palette_name in self.color_palettes:
                cmap = plt.cm.get_cmap(self.color_palettes[palette_name])
                return cmap(0.0)
            return '#1f77b4'
            
    def get_current_colormap(self):
        """Get the current colormap from internal settings."""
        palette_name = self.internal_settings['color_palette']
        return self.color_palettes.get(palette_name, 'viridis')
        
    def choose_custom_color(self):
        """Open color picker for custom color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.custom_color = color.name()
            self.palette_combo.setCurrentText("Custom")
            self.schedule_update()
            
    def export_plot(self, format_type):
        """Export the current plot."""
        if format_type == "clipboard":
            # Copy to clipboard
            # Render to pixmap
            pixmap = self.canvas.grab()
            QApplication.clipboard().setPixmap(pixmap)
            self.status_label.setText("Plot copied to clipboard")
            return
            
        # File export
        filters = {
            "pdf": "PDF Files (*.pdf)",
            "png": "PNG Files (*.png)",
            "svg": "SVG Files (*.svg)",
            "jpg": "JPEG Files (*.jpg)"
        }
        
        filename, _ = QFileDialog.getSaveFileName(
            self, f"Save Plot as {format_type.upper()}", 
            f"plot.{format_type}", filters.get(format_type, "All Files (*)")
        )
        
        if filename:
            try:
                dpi = self.dpi_spin.value()
                self.figure.savefig(filename, dpi=dpi, bbox_inches='tight', 
                                  facecolor='white', edgecolor='none')
                self.status_label.setText(f"Plot saved as {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to save plot: {str(e)}")
                
    def export_latex(self):
        """Export plot code for LaTeX."""
        # This would generate TikZ or PGFPlots code
        latex_code = self.generate_latex_code()
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save LaTeX Code", "plot.tex", "TeX Files (*.tex)"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(latex_code)
                self.status_label.setText(f"LaTeX code saved as {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to save LaTeX code: {str(e)}")
                
    def generate_latex_code(self):
        """Generate LaTeX/TikZ code for the current plot."""
        # Simplified LaTeX code generation
        # In a full implementation, this would analyze the current plot and generate appropriate TikZ code
        return """\\begin{tikzpicture}
\\begin{axis}[
    xlabel={""" + self.xlabel_edit.text() + """},
    ylabel={""" + self.ylabel_edit.text() + """},
    title={""" + self.title_edit.text() + """},
    grid=major,
]
% Add your data points here
\\addplot coordinates {
    % (x1,y1) (x2,y2) ...
};
\\end{axis}
\\end{tikzpicture}"""

    def apply_customization_settings(self, settings):
        """Apply settings from the customization dialog."""
        # Update internal settings with new values
        if 'title' in settings:
            self.internal_settings['title'] = settings['title']
        if 'xlabel' in settings:
            self.internal_settings['xlabel'] = settings['xlabel']
        if 'ylabel' in settings:
            self.internal_settings['ylabel'] = settings['ylabel']
        if 'fontsize' in settings:
            self.internal_settings['fontsize'] = settings['fontsize']
        if 'axis_fontsize' in settings:
            self.internal_settings['axis_fontsize'] = settings['axis_fontsize']
        if 'tick_fontsize' in settings:
            self.internal_settings['tick_fontsize'] = settings['tick_fontsize']
        if 'grid' in settings:
            self.internal_settings['grid'] = settings['grid']
        if 'legend' in settings:
            self.internal_settings['legend'] = settings['legend']
        if 'alpha' in settings:
            self.internal_settings['alpha'] = settings['alpha']
        if 'color_palette' in settings:
            self.internal_settings['color_palette'] = settings['color_palette']
        if 'plot_style' in settings:
            self.internal_settings['plot_style'] = settings['plot_style']
        if 'figure_size' in settings:
            self.internal_settings['figure_size'] = settings['figure_size']
        
        # Update plot-specific settings
        if 'line_settings' in settings:
            self.internal_settings['line_settings'].update(settings['line_settings'])
        if 'scatter_settings' in settings:
            self.internal_settings['scatter_settings'].update(settings['scatter_settings'])
        if 'bar_settings' in settings:
            self.internal_settings['bar_settings'].update(settings['bar_settings'])
        if 'hist_settings' in settings:
            self.internal_settings['hist_settings'].update(settings['hist_settings'])
        if 'axes_settings' in settings:
            self.internal_settings['axes_settings'].update(settings['axes_settings'])
        if 'multi_settings' in settings:
            self.internal_settings['multi_settings'].update(settings['multi_settings'])
            # Store subplot configurations for multi-plot access
            if 'subplot_configs' in settings['multi_settings']:
                self.subplot_configs_data = settings['multi_settings']['subplot_configs']
                print(f"DEBUG: Stored subplot configurations: {len(self.subplot_configs_data)} configs")
        
        # Sync UI to match updated internal settings
        self.sync_ui_to_internal_settings()
        
        # Trigger plot update to apply all changes
        self.schedule_update()


class PlotCustomizationDialog(QDialog):
    """Advanced plot customization dialog with plot-type-specific options."""
    
    def __init__(self, parent, plot_type):
        super().__init__(parent)
        self.plot_type = plot_type
        self.settings = {}
        
        self.setWindowTitle(f"Customize {plot_type.title()} Plot")
        self.setModal(True)
        self.resize(500, 600)
        
        self.setup_ui()
        self.load_current_settings()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Create tab widget for different customization categories
        self.tab_widget = QTabWidget()
        
        # General tab (always present)
        general_tab = self.create_general_tab()
        self.tab_widget.addTab(general_tab, "📊 General")
        
        # Plot-specific tabs
        if self.plot_type == "line":
            line_tab = self.create_line_tab()
            self.tab_widget.addTab(line_tab, "📈 Line Style")
        elif self.plot_type == "scatter":
            scatter_tab = self.create_scatter_tab()
            self.tab_widget.addTab(scatter_tab, "⚫ Scatter Points")
        elif self.plot_type == "bar":
            bar_tab = self.create_bar_tab()
            self.tab_widget.addTab(bar_tab, "📊 Bar Style")
        elif self.plot_type == "hist":
            hist_tab = self.create_histogram_tab()
            self.tab_widget.addTab(hist_tab, "📏 Histogram")
        elif self.plot_type in ["box", "violin"]:
            stats_tab = self.create_statistical_tab()
            self.tab_widget.addTab(stats_tab, "📦 Statistical")
        elif self.plot_type == "heatmap":
            heatmap_tab = self.create_heatmap_tab()
            self.tab_widget.addTab(heatmap_tab, "🔥 Heatmap")
        elif self.plot_type == "multi":
            multi_tab = self.create_multi_plot_tab()
            self.tab_widget.addTab(multi_tab, "🎯 Grid Layout")
        
        # Colors and styling tab
        colors_tab = self.create_colors_tab()
        self.tab_widget.addTab(colors_tab, "🎨 Colors")
        
        # Axes and labels tab
        axes_tab = self.create_axes_tab()
        self.tab_widget.addTab(axes_tab, "📐 Axes")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_btn)
        
        preview_btn = QPushButton("👁️ Preview")
        preview_btn.clicked.connect(self.preview_changes)
        button_layout.addWidget(preview_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("✅ Apply")
        apply_btn.clicked.connect(self.apply_settings)
        button_layout.addWidget(apply_btn)
        
        layout.addLayout(button_layout)
        
    def apply_settings(self):
        """Apply settings and close dialog."""
        # Store the current subplot configurations before closing
        print("DEBUG: apply_settings called - storing subplot configurations")
        
        # Make sure subplot configurations are up to date
        if hasattr(self, 'subplot_configs'):
            print(f"DEBUG: Found {len(self.subplot_configs)} subplot configs to store")
            for i, config in enumerate(self.subplot_configs):
                plot_type = config['plot_type_combo'].currentText()
                title = config['title_edit'].text()
                individual_enabled = config['axes_group'].isEnabled()
                print(f"DEBUG: Subplot {i}: type='{plot_type}', title='{title}', individual_enabled={individual_enabled}")
        else:
            print("DEBUG: No subplot_configs found!")
            
        # Close the dialog with accept
        self.accept()
        
    def create_general_tab(self):
        """Create general customization tab."""
        tab = QWidget()
        layout = QGridLayout(tab)
        
        # Title
        layout.addWidget(QLabel("Plot Title:"), 0, 0)
        self.title_edit = QLineEdit()
        layout.addWidget(self.title_edit, 0, 1)
        
        # Font size
        layout.addWidget(QLabel("Title Font Size:"), 1, 0)
        self.fontsize_spin = QSpinBox()
        self.fontsize_spin.setRange(8, 36)
        self.fontsize_spin.setValue(12)
        layout.addWidget(self.fontsize_spin, 1, 1)
        
        # Axis label font size
        layout.addWidget(QLabel("Axis Label Font Size:"), 2, 0)
        self.axis_fontsize_spin = QSpinBox()
        self.axis_fontsize_spin.setRange(6, 24)
        self.axis_fontsize_spin.setValue(10)
        layout.addWidget(self.axis_fontsize_spin, 2, 1)
        
        # Tick label font size
        layout.addWidget(QLabel("Tick Label Font Size:"), 3, 0)
        self.tick_fontsize_spin = QSpinBox()
        self.tick_fontsize_spin.setRange(6, 20)
        self.tick_fontsize_spin.setValue(8)
        layout.addWidget(self.tick_fontsize_spin, 3, 1)
        
        # Grid
        self.grid_check = QCheckBox("Show Grid")
        self.grid_check.setChecked(True)
        layout.addWidget(self.grid_check, 4, 0, 1, 2)
        
        # Legend
        self.legend_check = QCheckBox("Show Legend")
        self.legend_check.setChecked(True)
        layout.addWidget(self.legend_check, 5, 0, 1, 2)
        
        # Transparency
        layout.addWidget(QLabel("Transparency:"), 6, 0)
        self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setRange(10, 100)
        self.alpha_slider.setValue(80)
        self.alpha_label = QLabel("80%")
        self.alpha_slider.valueChanged.connect(lambda v: self.alpha_label.setText(f"{v}%"))
        alpha_layout = QHBoxLayout()
        alpha_layout.addWidget(self.alpha_slider)
        alpha_layout.addWidget(self.alpha_label)
        layout.addLayout(alpha_layout, 6, 1)
        
        # Figure size
        layout.addWidget(QLabel("Figure Size:"), 7, 0)
        size_layout = QHBoxLayout()
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(4, 20)
        self.width_spin.setValue(10)
        self.width_spin.setSuffix(" in")
        size_layout.addWidget(self.width_spin)
        size_layout.addWidget(QLabel("×"))
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(3, 15)
        self.height_spin.setValue(6)
        self.height_spin.setSuffix(" in")
        size_layout.addWidget(self.height_spin)
        layout.addLayout(size_layout, 7, 1)
        
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 8, 0)
        return tab
        
    def create_line_tab(self):
        """Create line plot specific customization tab."""
        tab = QWidget()
        layout = QGridLayout(tab)
        
        # Line width
        layout.addWidget(QLabel("Line Width:"), 0, 0)
        self.linewidth_spin = QDoubleSpinBox()
        self.linewidth_spin.setRange(0.5, 10.0)
        self.linewidth_spin.setValue(2.0)
        self.linewidth_spin.setSingleStep(0.5)
        layout.addWidget(self.linewidth_spin, 0, 1)
        
        # Line style
        layout.addWidget(QLabel("Line Style:"), 1, 0)
        self.linestyle_combo = QComboBox()
        self.linestyle_combo.addItems(["-", "--", "-.", ":", "None"])
        layout.addWidget(self.linestyle_combo, 1, 1)
        
        # Marker style
        layout.addWidget(QLabel("Marker Style:"), 2, 0)
        self.marker_combo = QComboBox()
        self.marker_combo.addItems(["None", "o", "s", "^", "v", "<", ">", "D", "p", "*", "+", "x"])
        layout.addWidget(self.marker_combo, 2, 1)
        
        # Marker size
        layout.addWidget(QLabel("Marker Size:"), 3, 0)
        self.markersize_spin = QSpinBox()
        self.markersize_spin.setRange(1, 20)
        self.markersize_spin.setValue(6)
        layout.addWidget(self.markersize_spin, 3, 1)
        
        # Error bars
        self.errorbar_check = QCheckBox("Show Error Bars")
        layout.addWidget(self.errorbar_check, 4, 0, 1, 2)
        
        # Smooth line
        self.smooth_check = QCheckBox("Smooth Line (Interpolation)")
        layout.addWidget(self.smooth_check, 5, 0, 1, 2)
        
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 6, 0)
        return tab
        
    def create_scatter_tab(self):
        """Create scatter plot specific customization tab."""
        tab = QWidget()
        layout = QGridLayout(tab)
        
        # Marker style
        layout.addWidget(QLabel("Marker Style:"), 0, 0)
        self.marker_combo = QComboBox()
        self.marker_combo.addItems(["o", "s", "^", "v", "<", ">", "D", "p", "*", "+", "x"])
        layout.addWidget(self.marker_combo, 0, 1)
        
        # Marker size
        layout.addWidget(QLabel("Marker Size:"), 1, 0)
        self.markersize_spin = QSpinBox()
        self.markersize_spin.setRange(1, 30)
        self.markersize_spin.setValue(6)
        layout.addWidget(self.markersize_spin, 1, 1)
        
        # Size scaling
        layout.addWidget(QLabel("Size Scaling:"), 2, 0)
        self.size_scale_spin = QDoubleSpinBox()
        self.size_scale_spin.setRange(0.1, 5.0)
        self.size_scale_spin.setValue(1.0)
        self.size_scale_spin.setSingleStep(0.1)
        layout.addWidget(self.size_scale_spin, 2, 1)
        
        # Edge width
        layout.addWidget(QLabel("Edge Width:"), 3, 0)
        self.edge_width_spin = QDoubleSpinBox()
        self.edge_width_spin.setRange(0.0, 3.0)
        self.edge_width_spin.setValue(0.8)
        self.edge_width_spin.setSingleStep(0.1)
        layout.addWidget(self.edge_width_spin, 3, 1)
        
        # Jitter
        self.jitter_check = QCheckBox("Add Jitter (Random Offset)")
        layout.addWidget(self.jitter_check, 4, 0, 1, 2)
        
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 5, 0)
        return tab
        
    def create_bar_tab(self):
        """Create bar plot specific customization tab."""
        tab = QWidget()
        layout = QGridLayout(tab)
        
        # Bar width
        layout.addWidget(QLabel("Bar Width:"), 0, 0)
        self.bar_width_spin = QDoubleSpinBox()
        self.bar_width_spin.setRange(0.1, 2.0)
        self.bar_width_spin.setValue(0.8)
        self.bar_width_spin.setSingleStep(0.1)
        layout.addWidget(self.bar_width_spin, 0, 1)
        
        # Edge width
        layout.addWidget(QLabel("Edge Width:"), 1, 0)
        self.edge_width_spin = QDoubleSpinBox()
        self.edge_width_spin.setRange(0.0, 3.0)
        self.edge_width_spin.setValue(1.0)
        self.edge_width_spin.setSingleStep(0.1)
        layout.addWidget(self.edge_width_spin, 1, 1)
        
        # Bar orientation
        layout.addWidget(QLabel("Orientation:"), 2, 0)
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["Vertical", "Horizontal"])
        layout.addWidget(self.orientation_combo, 2, 1)
        
        # Error bars
        self.errorbar_check = QCheckBox("Show Error Bars")
        layout.addWidget(self.errorbar_check, 3, 0, 1, 2)
        
        # Value labels
        self.value_labels_check = QCheckBox("Show Value Labels")
        layout.addWidget(self.value_labels_check, 4, 0, 1, 2)
        
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 5, 0)
        return tab
        
    def create_histogram_tab(self):
        """Create histogram specific customization tab."""
        tab = QWidget()
        layout = QGridLayout(tab)
        
        # Number of bins
        layout.addWidget(QLabel("Number of Bins:"), 0, 0)
        self.bins_spin = QSpinBox()
        self.bins_spin.setRange(5, 100)
        self.bins_spin.setValue(20)
        layout.addWidget(self.bins_spin, 0, 1)
        
        # Bin method
        layout.addWidget(QLabel("Bin Method:"), 1, 0)
        self.bin_method_combo = QComboBox()
        self.bin_method_combo.addItems(["auto", "equal-width", "equal-frequency", "sqrt", "sturges", "scott"])
        layout.addWidget(self.bin_method_combo, 1, 1)
        
        # Density
        self.density_check = QCheckBox("Show Density (Normalize)")
        layout.addWidget(self.density_check, 2, 0, 1, 2)
        
        # Cumulative
        self.cumulative_check = QCheckBox("Cumulative Histogram")
        layout.addWidget(self.cumulative_check, 3, 0, 1, 2)
        
        # Step histogram
        self.step_check = QCheckBox("Step Histogram")
        layout.addWidget(self.step_check, 4, 0, 1, 2)
        
        # Statistics overlay
        self.stats_check = QCheckBox("Show Statistics (Mean, Std)")
        layout.addWidget(self.stats_check, 5, 0, 1, 2)
        
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 6, 0)
        return tab
        
    def create_statistical_tab(self):
        """Create statistical plot customization tab."""
        tab = QWidget()
        layout = QGridLayout(tab)
        
        # Show outliers
        self.outliers_check = QCheckBox("Show Outliers")
        self.outliers_check.setChecked(True)
        layout.addWidget(self.outliers_check, 0, 0, 1, 2)
        
        # Show means
        self.means_check = QCheckBox("Show Means")
        layout.addWidget(self.means_check, 1, 0, 1, 2)
        
        # Notched boxes
        self.notch_check = QCheckBox("Notched Boxes")
        layout.addWidget(self.notch_check, 2, 0, 1, 2)
        
        # Box width
        layout.addWidget(QLabel("Box Width:"), 3, 0)
        self.box_width_spin = QDoubleSpinBox()
        self.box_width_spin.setRange(0.1, 2.0)
        self.box_width_spin.setValue(0.8)
        self.box_width_spin.setSingleStep(0.1)
        layout.addWidget(self.box_width_spin, 3, 1)
        
        # Whisker length
        layout.addWidget(QLabel("Whisker Length:"), 4, 0)
        self.whisker_spin = QDoubleSpinBox()
        self.whisker_spin.setRange(1.0, 3.0)
        self.whisker_spin.setValue(1.5)
        self.whisker_spin.setSingleStep(0.1)
        layout.addWidget(self.whisker_spin, 4, 1)
        
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 5, 0)
        return tab
        
    def create_heatmap_tab(self):
        """Create heatmap specific customization tab."""
        tab = QWidget()
        layout = QGridLayout(tab)
        
        # Annotation
        self.annot_check = QCheckBox("Show Value Annotations")
        self.annot_check.setChecked(True)
        layout.addWidget(self.annot_check, 0, 0, 1, 2)
        
        # Center colormap
        layout.addWidget(QLabel("Center Value:"), 1, 0)
        self.center_spin = QDoubleSpinBox()
        self.center_spin.setRange(-10, 10)
        self.center_spin.setValue(0)
        layout.addWidget(self.center_spin, 1, 1)
        
        # Colorbar
        self.colorbar_check = QCheckBox("Show Colorbar")
        self.colorbar_check.setChecked(True)
        layout.addWidget(self.colorbar_check, 2, 0, 1, 2)
        
        # Square cells
        self.square_check = QCheckBox("Square Cells")
        layout.addWidget(self.square_check, 3, 0, 1, 2)
        
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 4, 0)
        return tab
        
    def create_multi_plot_tab(self):
        """Create multi-plot grid configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create scrollable area for complex configuration
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        
        # Grid configuration
        grid_group = QGroupBox("Grid Configuration")
        grid_layout = QGridLayout(grid_group)
        
        # Grid size controls
        grid_layout.addWidget(QLabel("Rows:"), 0, 0)
        self.grid_rows_dialog = QSpinBox()
        self.grid_rows_dialog.setRange(1, 4)
        self.grid_rows_dialog.setValue(self.parent().grid_rows_spin.value())
        grid_layout.addWidget(self.grid_rows_dialog, 0, 1)
        
        grid_layout.addWidget(QLabel("Columns:"), 0, 2)
        self.grid_cols_dialog = QSpinBox()
        self.grid_cols_dialog.setRange(1, 4)
        self.grid_cols_dialog.setValue(self.parent().grid_cols_spin.value())
        grid_layout.addWidget(self.grid_cols_dialog, 0, 3)
        
        # Spacing controls
        grid_layout.addWidget(QLabel("H-Spacing:"), 1, 0)
        self.hspace_spin = QDoubleSpinBox()
        self.hspace_spin.setRange(0.0, 1.0)
        self.hspace_spin.setValue(0.3)
        self.hspace_spin.setSingleStep(0.1)
        grid_layout.addWidget(self.hspace_spin, 1, 1)
        
        grid_layout.addWidget(QLabel("V-Spacing:"), 1, 2)
        self.wspace_spin = QDoubleSpinBox()
        self.wspace_spin.setRange(0.0, 1.0)
        self.wspace_spin.setValue(0.3)
        self.wspace_spin.setSingleStep(0.1)
        grid_layout.addWidget(self.wspace_spin, 1, 3)
        
        scroll_layout.addWidget(grid_group, 0, 0, 1, 2)
        
        # General data selection for all subplots
        data_group = QGroupBox("General Data Selection (applies to all subplots unless individually overridden)")
        data_layout = QGridLayout(data_group)
        
        # Default X column for all subplots
        data_layout.addWidget(QLabel("Default X Column:"), 0, 0)
        self.default_x_combo = QComboBox()
        if hasattr(self.parent(), 'data_manager') and self.parent().data_manager.has_data():
            self.default_x_combo.addItems(self.parent().data_manager.get_analysis_numeric_columns())
            # Set to current main selection if available
            if hasattr(self.parent(), 'x_combo'):
                current_x = self.parent().x_combo.currentText()
                if current_x in self.parent().data_manager.get_analysis_numeric_columns():
                    self.default_x_combo.setCurrentText(current_x)
        data_layout.addWidget(self.default_x_combo, 0, 1)
        
        # Default Y column for all subplots
        data_layout.addWidget(QLabel("Default Y Column:"), 1, 0)
        self.default_y_combo = QComboBox()
        if hasattr(self.parent(), 'data_manager') and self.parent().data_manager.has_data():
            self.default_y_combo.addItems(self.parent().data_manager.get_analysis_numeric_columns())
            # Set to current main selection if available
            if hasattr(self.parent(), 'y_combo'):
                current_y = self.parent().y_combo.currentText()
                if current_y in self.parent().data_manager.get_analysis_numeric_columns():
                    self.default_y_combo.setCurrentText(current_y)
        data_layout.addWidget(self.default_y_combo, 1, 1)
        
        # Button to apply defaults to all subplots
        apply_defaults_btn = QPushButton("📋 Apply to All Subplots")
        apply_defaults_btn.clicked.connect(self.apply_defaults_to_all_subplots)
        data_layout.addWidget(apply_defaults_btn, 2, 0, 1, 2)
        
        scroll_layout.addWidget(data_group, 1, 0, 1, 2)
        
        # Individual subplot configuration
        self.subplot_group = QGroupBox("Individual Subplot Configuration")
        self.subplot_layout = QVBoxLayout(self.subplot_group)
        scroll_layout.addWidget(self.subplot_group, 2, 0, 1, 2)
        
        # Individual subplot styling options
        self.individual_styling_check = QCheckBox("Enable individual styling for each subplot")
        self.individual_styling_check.setChecked(True)  # Enable by default for multi-plot
        self.individual_styling_check.toggled.connect(self.toggle_individual_styling)
        scroll_layout.addWidget(self.individual_styling_check, 3, 0, 1, 2)
        
        # This will be populated dynamically based on grid size
        self.subplot_configs = []
        self.update_subplot_configs()
        
        # Connect grid size changes to update subplot controls
        self.grid_rows_dialog.valueChanged.connect(self.update_subplot_configs)
        self.grid_cols_dialog.valueChanged.connect(self.update_subplot_configs)
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(400)
        layout.addWidget(scroll)
        
        return tab
        
    def apply_defaults_to_all_subplots(self):
        """Apply the default X/Y columns to all individual subplots."""
        if not hasattr(self, 'subplot_configs') or not hasattr(self, 'default_x_combo') or not hasattr(self, 'default_y_combo'):
            return
            
        default_x = self.default_x_combo.currentText()
        default_y = self.default_y_combo.currentText()
        
        print(f"DEBUG: Applying defaults to all subplots: X='{default_x}', Y='{default_y}'")
        
        for i, config in enumerate(self.subplot_configs):
            if 'x_column_combo' in config:
                config['x_column_combo'].setCurrentText(default_x)
                print(f"DEBUG: Set subplot {i} X column to '{default_x}'")
            if 'y_column_combo' in config:
                config['y_column_combo'].setCurrentText(default_y)
                print(f"DEBUG: Set subplot {i} Y column to '{default_y}'")
        
        print("DEBUG: Applied default columns to all subplots")
        
    def update_subplot_configs(self):
        """Update individual subplot configuration controls."""
        print("DEBUG: update_subplot_configs called")
        
        # Clear existing controls
        for config in self.subplot_configs:
            config['widget'].setParent(None)
        self.subplot_configs.clear()
        
        # Clear layout
        while self.subplot_layout.count():
            child = self.subplot_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        
        rows = self.grid_rows_dialog.value()
        cols = self.grid_cols_dialog.value()
        
        print(f"DEBUG: Creating subplot configs for {rows}x{cols} grid")
        
        plot_types = ["line", "scatter", "bar", "hist", "box", "violin"]
        
        for i in range(rows):
            for j in range(cols):
                subplot_num = i * cols + j + 1
                
                # Create group for this subplot
                subplot_widget = QGroupBox(f"Subplot ({i+1},{j+1})")
                subplot_layout = QGridLayout(subplot_widget)
                
                # Plot type selection
                subplot_layout.addWidget(QLabel("Plot Type:"), 0, 0)
                plot_type_combo = QComboBox()
                plot_type_combo.addItems([t.title() for t in plot_types])
                subplot_layout.addWidget(plot_type_combo, 0, 1)
                
                # X and Y column selection for this subplot
                subplot_layout.addWidget(QLabel("X Column:"), 1, 0)
                x_column_combo = QComboBox()
                # Get available columns from parent
                if hasattr(self.parent(), 'data_manager') and self.parent().data_manager.has_data():
                    x_column_combo.addItems(self.parent().data_manager.get_analysis_numeric_columns())
                    # Set default from general selection if available
                    if hasattr(self, 'default_x_combo') and self.default_x_combo.currentText():
                        default_x = self.default_x_combo.currentText()
                        if default_x in self.parent().data_manager.get_analysis_numeric_columns():
                            x_column_combo.setCurrentText(default_x)
                    elif x_column_combo.count() > 0:
                        x_column_combo.setCurrentIndex(0)
                subplot_layout.addWidget(x_column_combo, 1, 1)
                
                subplot_layout.addWidget(QLabel("Y Column:"), 2, 0)
                y_column_combo = QComboBox()
                if hasattr(self.parent(), 'data_manager') and self.parent().data_manager.has_data():
                    y_column_combo.addItems(self.parent().data_manager.get_analysis_numeric_columns())
                    # Set default from general selection if available
                    if hasattr(self, 'default_y_combo') and self.default_y_combo.currentText():
                        default_y = self.default_y_combo.currentText()
                        if default_y in self.parent().data_manager.get_analysis_numeric_columns():
                            y_column_combo.setCurrentText(default_y)
                    elif y_column_combo.count() > 1:
                        y_column_combo.setCurrentIndex(1)
                    elif y_column_combo.count() > 0:
                        y_column_combo.setCurrentIndex(0)
                subplot_layout.addWidget(y_column_combo, 2, 1)
                
                # Title
                subplot_layout.addWidget(QLabel("Title:"), 3, 0)
                title_edit = QLineEdit()
                title_edit.setPlaceholderText(f"Subplot {subplot_num} Title")
                subplot_layout.addWidget(title_edit, 3, 1)
                
                # Individual axes settings (enabled only when individual styling is on)
                axes_group = QGroupBox("Individual Axes Settings")
                axes_layout = QGridLayout(axes_group)
                
                # X-axis settings
                axes_layout.addWidget(QLabel("X-Label:"), 0, 0)
                xlabel_edit = QLineEdit()
                axes_layout.addWidget(xlabel_edit, 0, 1)
                
                axes_layout.addWidget(QLabel("Y-Label:"), 1, 0)
                ylabel_edit = QLineEdit()
                axes_layout.addWidget(ylabel_edit, 1, 1)
                
                # Scale settings
                axes_layout.addWidget(QLabel("X-Scale:"), 2, 0)
                x_scale_combo = QComboBox()
                x_scale_combo.addItems(["linear", "log", "symlog"])
                axes_layout.addWidget(x_scale_combo, 2, 1)
                
                axes_layout.addWidget(QLabel("Y-Scale:"), 3, 0)
                y_scale_combo = QComboBox()
                y_scale_combo.addItems(["linear", "log", "symlog"])
                axes_layout.addWidget(y_scale_combo, 3, 1)
                
                # Limit settings
                xlim_layout = QHBoxLayout()
                xlim_min = QDoubleSpinBox()
                xlim_min.setRange(-1e6, 1e6)
                xlim_min.setValue(0)
                xlim_max = QDoubleSpinBox()
                xlim_max.setRange(-1e6, 1e6)
                xlim_max.setValue(10)
                xlim_layout.addWidget(QLabel("X-Lim:"))
                xlim_layout.addWidget(xlim_min)
                xlim_layout.addWidget(QLabel("to"))
                xlim_layout.addWidget(xlim_max)
                axes_layout.addLayout(xlim_layout, 4, 0, 1, 2)
                
                ylim_layout = QHBoxLayout()
                ylim_min = QDoubleSpinBox()
                ylim_min.setRange(-1e6, 1e6)
                ylim_min.setValue(0)
                ylim_max = QDoubleSpinBox()
                ylim_max.setRange(-1e6, 1e6)
                ylim_max.setValue(10)
                ylim_layout.addWidget(QLabel("Y-Lim:"))
                ylim_layout.addWidget(ylim_min)
                ylim_layout.addWidget(QLabel("to"))
                ylim_layout.addWidget(ylim_max)
                axes_layout.addLayout(ylim_layout, 5, 0, 1, 2)
                
                # Individual styling settings
                style_group = QGroupBox("Individual Plot Styling")
                style_layout = QGridLayout(style_group)
                
                # Color
                style_layout.addWidget(QLabel("Color:"), 0, 0)
                color_combo = QComboBox()
                color_combo.addItems(["Auto", "Blue", "Red", "Green", "Orange", "Purple", "Custom"])
                style_layout.addWidget(color_combo, 0, 1)
                
                # Alpha
                style_layout.addWidget(QLabel("Alpha:"), 1, 0)
                alpha_spin = QDoubleSpinBox()
                alpha_spin.setRange(0.1, 1.0)
                alpha_spin.setValue(0.8)
                alpha_spin.setSingleStep(0.1)
                style_layout.addWidget(alpha_spin, 1, 1)
                
                # Plot-specific styling (will be shown/hidden based on plot type)
                linewidth_spin = QDoubleSpinBox()
                linewidth_spin.setRange(0.5, 10.0)
                linewidth_spin.setValue(2.0)
                
                markersize_spin = QSpinBox()
                markersize_spin.setRange(1, 20)
                markersize_spin.setValue(6)
                
                bins_spin = QSpinBox()
                bins_spin.setRange(5, 100)
                bins_spin.setValue(20)
                
                bar_width_spin = QDoubleSpinBox()
                bar_width_spin.setRange(0.1, 2.0)
                bar_width_spin.setValue(0.8)
                
                style_layout.addWidget(QLabel("Line Width:"), 2, 0)
                style_layout.addWidget(linewidth_spin, 2, 1)
                style_layout.addWidget(QLabel("Marker Size:"), 3, 0)
                style_layout.addWidget(markersize_spin, 3, 1)
                style_layout.addWidget(QLabel("Bins:"), 4, 0)
                style_layout.addWidget(bins_spin, 4, 1)
                style_layout.addWidget(QLabel("Bar Width:"), 5, 0)
                style_layout.addWidget(bar_width_spin, 5, 1)
                
                # Add groups to subplot widget
                subplot_layout.addWidget(axes_group, 4, 0, 1, 2)
                subplot_layout.addWidget(style_group, 5, 0, 1, 2)
                
                # Initially disable individual settings
                axes_group.setEnabled(False)
                style_group.setEnabled(False)
                
                # Store subplot configuration
                config = {
                    'row': i,
                    'col': j,
                    'widget': subplot_widget,
                    'plot_type_combo': plot_type_combo,
                    'x_column_combo': x_column_combo,
                    'y_column_combo': y_column_combo,
                    'title_edit': title_edit,
                    'xlabel_edit': xlabel_edit,
                    'ylabel_edit': ylabel_edit,
                    'x_scale_combo': x_scale_combo,
                    'y_scale_combo': y_scale_combo,
                    'xlim_min': xlim_min,
                    'xlim_max': xlim_max,
                    'ylim_min': ylim_min,
                    'ylim_max': ylim_max,
                    'color_combo': color_combo,
                    'alpha_spin': alpha_spin,
                    'linewidth_spin': linewidth_spin,
                    'markersize_spin': markersize_spin,
                    'bins_spin': bins_spin,
                    'bar_width_spin': bar_width_spin,
                    'axes_group': axes_group,
                    'style_group': style_group
                }
                
                self.subplot_configs.append(config)
                self.subplot_layout.addWidget(subplot_widget)
                
        print(f"DEBUG: Created {len(self.subplot_configs)} subplot configurations")
        
        # Trigger the individual styling toggle to enable controls if checkbox is checked
        if hasattr(self, 'individual_styling_check'):
            self.toggle_individual_styling(self.individual_styling_check.isChecked())
        
    def toggle_individual_styling(self, enabled):
        """Enable/disable individual subplot styling."""
        print(f"DEBUG: toggle_individual_styling called with enabled={enabled}")
        for i, config in enumerate(self.subplot_configs):
            config['axes_group'].setEnabled(enabled)
            config['style_group'].setEnabled(enabled)
            print(f"DEBUG: Subplot {i} axes_group enabled: {config['axes_group'].isEnabled()}")
        
    def create_colors_tab(self):
        """Create colors and styling customization tab."""
        tab = QWidget()
        layout = QGridLayout(tab)
        
        # Color palette
        layout.addWidget(QLabel("Color Palette:"), 0, 0)
        self.palette_combo = QComboBox()
        self.palette_combo.addItems([
            "Default", "Scientific", "Colorblind", "Viridis", 
            "Plasma", "Cool", "Warm", "Custom"
        ])
        layout.addWidget(self.palette_combo, 0, 1)
        
        # Custom color button
        self.custom_color_btn = QPushButton("🎨 Choose Custom Color")
        self.custom_color_btn.clicked.connect(self.choose_custom_color)
        layout.addWidget(self.custom_color_btn, 1, 0, 1, 2)
        
        # Color reverse
        self.reverse_colors_check = QCheckBox("Reverse Color Order")
        layout.addWidget(self.reverse_colors_check, 2, 0, 1, 2)
        
        # Plot style
        layout.addWidget(QLabel("Plot Style:"), 3, 0)
        self.style_combo = QComboBox()
        self.style_combo.addItems([
            "default", "scientific", "publication", "dark", "minimal"
        ])
        layout.addWidget(self.style_combo, 3, 1)
        
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 4, 0)
        return tab
        
    def create_axes_tab(self):
        """Create axes and labels customization tab."""
        tab = QWidget()
        layout = QGridLayout(tab)
        
        # X-axis label
        layout.addWidget(QLabel("X-axis Label:"), 0, 0)
        self.xlabel_edit = QLineEdit()
        layout.addWidget(self.xlabel_edit, 0, 1)
        
        # Y-axis label
        layout.addWidget(QLabel("Y-axis Label:"), 1, 0)
        self.ylabel_edit = QLineEdit()
        layout.addWidget(self.ylabel_edit, 1, 1)
        
        # Log scales
        self.logx_check = QCheckBox("Logarithmic X-axis")
        layout.addWidget(self.logx_check, 2, 0, 1, 2)
        
        self.logy_check = QCheckBox("Logarithmic Y-axis")
        layout.addWidget(self.logy_check, 3, 0, 1, 2)
        
        # Scale types
        layout.addWidget(QLabel("X-axis Scale Type:"), 4, 0)
        self.x_scale_combo = QComboBox()
        self.x_scale_combo.addItems(["linear", "log", "symlog", "logit"])
        layout.addWidget(self.x_scale_combo, 4, 1)
        
        layout.addWidget(QLabel("Y-axis Scale Type:"), 5, 0)
        self.y_scale_combo = QComboBox()
        self.y_scale_combo.addItems(["linear", "log", "symlog", "logit"])
        layout.addWidget(self.y_scale_combo, 5, 1)
        
        # Scientific notation
        self.scientific_check = QCheckBox("Scientific Notation")
        layout.addWidget(self.scientific_check, 6, 0, 1, 2)
        
        # Aspect ratio
        layout.addWidget(QLabel("Aspect Ratio:"), 7, 0)
        self.aspect_combo = QComboBox()
        self.aspect_combo.addItems(["auto", "equal", "1:1", "4:3", "16:9"])
        layout.addWidget(self.aspect_combo, 7, 1)
        
        # Axis limits with auto checkbox
        layout.addWidget(QLabel("X-axis Limits:"), 8, 0)
        x_limits_layout = QVBoxLayout()
        self.x_auto_check = QCheckBox("Auto X-limits")
        self.x_auto_check.setChecked(True)
        self.x_auto_check.toggled.connect(self.toggle_x_limits)
        x_limits_layout.addWidget(self.x_auto_check)
        
        x_manual_layout = QHBoxLayout()
        self.x_min_spin = QDoubleSpinBox()
        self.x_min_spin.setRange(-1e6, 1e6)
        self.x_min_spin.setValue(0)
        self.x_min_spin.setEnabled(False)
        x_manual_layout.addWidget(QLabel("Min:"))
        x_manual_layout.addWidget(self.x_min_spin)
        x_manual_layout.addWidget(QLabel("Max:"))
        self.x_max_spin = QDoubleSpinBox()
        self.x_max_spin.setRange(-1e6, 1e6)
        self.x_max_spin.setValue(10)
        self.x_max_spin.setEnabled(False)
        x_manual_layout.addWidget(self.x_max_spin)
        x_limits_layout.addLayout(x_manual_layout)
        layout.addLayout(x_limits_layout, 8, 1)
        
        layout.addWidget(QLabel("Y-axis Limits:"), 9, 0)
        y_limits_layout = QVBoxLayout()
        self.y_auto_check = QCheckBox("Auto Y-limits")
        self.y_auto_check.setChecked(True)
        self.y_auto_check.toggled.connect(self.toggle_y_limits)
        y_limits_layout.addWidget(self.y_auto_check)
        
        y_manual_layout = QHBoxLayout()
        self.y_min_spin = QDoubleSpinBox()
        self.y_min_spin.setRange(-1e6, 1e6)
        self.y_min_spin.setValue(0)
        self.y_min_spin.setEnabled(False)
        y_manual_layout.addWidget(QLabel("Min:"))
        y_manual_layout.addWidget(self.y_min_spin)
        y_manual_layout.addWidget(QLabel("Max:"))
        self.y_max_spin = QDoubleSpinBox()
        self.y_max_spin.setRange(-1e6, 1e6)
        self.y_max_spin.setValue(10)
        self.y_max_spin.setEnabled(False)
        y_manual_layout.addWidget(self.y_max_spin)
        y_limits_layout.addLayout(y_manual_layout)
        layout.addLayout(y_limits_layout, 9, 1)
        
        # Tick control
        layout.addWidget(QLabel("X-axis Ticks:"), 10, 0)
        x_ticks_layout = QHBoxLayout()
        self.x_tick_count = QSpinBox()
        self.x_tick_count.setRange(2, 20)
        self.x_tick_count.setValue(5)
        x_ticks_layout.addWidget(QLabel("Count:"))
        x_ticks_layout.addWidget(self.x_tick_count)
        layout.addLayout(x_ticks_layout, 10, 1)
        
        layout.addWidget(QLabel("Y-axis Ticks:"), 11, 0)
        y_ticks_layout = QHBoxLayout()
        self.y_tick_count = QSpinBox()
        self.y_tick_count.setRange(2, 20)
        self.y_tick_count.setValue(5)
        y_ticks_layout.addWidget(QLabel("Count:"))
        y_ticks_layout.addWidget(self.y_tick_count)
        layout.addLayout(y_ticks_layout, 11, 1)
        
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 12, 0)
        return tab
        
    def toggle_x_limits(self, checked):
        """Toggle X-axis limit controls."""
        self.x_min_spin.setEnabled(not checked)
        self.x_max_spin.setEnabled(not checked)
        
    def toggle_y_limits(self, checked):
        """Toggle Y-axis limit controls."""
        self.y_min_spin.setEnabled(not checked)
        self.y_max_spin.setEnabled(not checked)
        
    def load_current_settings(self):
        """Load current settings from the parent plotting tab."""
        parent = self.parent()
        if hasattr(parent, 'title_edit'):
            self.title_edit.setText(parent.title_edit.text())
        if hasattr(parent, 'xlabel_edit'):
            self.xlabel_edit.setText(parent.xlabel_edit.text())
        if hasattr(parent, 'ylabel_edit'):
            self.ylabel_edit.setText(parent.ylabel_edit.text())
        if hasattr(parent, 'fontsize_spin'):
            self.fontsize_spin.setValue(parent.fontsize_spin.value())
        if hasattr(parent, 'grid_check'):
            self.grid_check.setChecked(parent.grid_check.isChecked())
        if hasattr(parent, 'legend_check'):
            self.legend_check.setChecked(parent.legend_check.isChecked())
        if hasattr(parent, 'alpha_slider'):
            self.alpha_slider.setValue(parent.alpha_slider.value())
        if hasattr(parent, 'palette_combo'):
            self.palette_combo.setCurrentText(parent.palette_combo.currentText())
        if hasattr(parent, 'style_combo'):
            self.style_combo.setCurrentText(parent.style_combo.currentText())
            
        # Load plot-specific settings
        if self.plot_type == "line":
            if hasattr(parent, 'linewidth_spin'):
                self.linewidth_spin.setValue(parent.linewidth_spin.value())
            if hasattr(parent, 'linestyle_combo'):
                self.linestyle_combo.setCurrentText(parent.linestyle_combo.currentText())
            if hasattr(parent, 'marker_combo'):
                self.marker_combo.setCurrentText(parent.marker_combo.currentText())
            if hasattr(parent, 'markersize_spin'):
                self.markersize_spin.setValue(parent.markersize_spin.value())
                
        elif self.plot_type == "scatter":
            if hasattr(parent, 'marker_combo'):
                self.marker_combo.setCurrentText(parent.marker_combo.currentText())
            if hasattr(parent, 'markersize_spin'):
                self.markersize_spin.setValue(parent.markersize_spin.value())
                
        elif self.plot_type == "bar":
            if hasattr(parent, 'bar_width_spin'):
                self.bar_width_spin.setValue(parent.bar_width_spin.value())
                
        elif self.plot_type == "hist":
            if hasattr(parent, 'bins_spin'):
                self.bins_spin.setValue(parent.bins_spin.value())
        
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        # Reset general settings
        self.title_edit.clear()
        self.fontsize_spin.setValue(12)
        self.grid_check.setChecked(True)
        self.legend_check.setChecked(True)
        self.alpha_slider.setValue(80)
        self.width_spin.setValue(10)
        self.height_spin.setValue(6)
        
        # Reset plot-specific settings
        if self.plot_type == "line":
            self.linewidth_spin.setValue(2.0)
            self.linestyle_combo.setCurrentText("-")
            self.marker_combo.setCurrentText("None")
            self.markersize_spin.setValue(6)
        elif self.plot_type == "scatter":
            self.marker_combo.setCurrentText("o")
            self.markersize_spin.setValue(6)
        elif self.plot_type == "bar":
            self.bar_width_spin.setValue(0.8)
        elif self.plot_type == "hist":
            self.bins_spin.setValue(20)
            
    def preview_changes(self):
        """Preview the changes without applying them."""
        # Get current settings and apply them temporarily
        settings = self.get_settings()
        parent = self.parent()
        if hasattr(parent, 'apply_customization_settings'):
            # Store current state
            self.temp_settings = {}
            # Apply preview settings
            parent.apply_customization_settings(settings)
            parent.schedule_update()
            
    def choose_custom_color(self):
        """Choose a custom color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.palette_combo.setCurrentText("Custom")
            # Store the custom color for later use
            self.custom_color = color.name()
    
    def get_settings(self):
        """Get all customization settings as a dictionary."""
        settings = {
            'title': self.title_edit.text(),
            'xlabel': self.xlabel_edit.text(),
            'ylabel': self.ylabel_edit.text(),
            'fontsize': self.fontsize_spin.value(),
            'axis_fontsize': self.axis_fontsize_spin.value(),
            'tick_fontsize': self.tick_fontsize_spin.value(),
            'grid': self.grid_check.isChecked(),
            'legend': self.legend_check.isChecked(),
            'alpha': self.alpha_slider.value() / 100.0,
            'color_palette': self.palette_combo.currentText(),
            'plot_style': self.style_combo.currentText(),
            'figure_size': (self.width_spin.value(), self.height_spin.value())
        }
        
        # Add plot-specific settings
        if self.plot_type == "line":
            settings['line_settings'] = {
                'linewidth': self.linewidth_spin.value(),
                'linestyle': self.linestyle_combo.currentText(),
                'marker': self.marker_combo.currentText(),
                'markersize': self.markersize_spin.value(),
                'errorbar': self.errorbar_check.isChecked() if hasattr(self, 'errorbar_check') else False,
                'smooth': self.smooth_check.isChecked() if hasattr(self, 'smooth_check') else False
            }
        elif self.plot_type == "scatter":
            settings['scatter_settings'] = {
                'marker': self.marker_combo.currentText(),
                'markersize': self.markersize_spin.value(),
                'size_scale': self.size_scale_spin.value() if hasattr(self, 'size_scale_spin') else 1.0,
                'edge_width': self.edge_width_spin.value() if hasattr(self, 'edge_width_spin') else 0.8,
                'jitter': self.jitter_check.isChecked() if hasattr(self, 'jitter_check') else False
            }
        elif self.plot_type == "bar":
            settings['bar_settings'] = {
                'bar_width': self.bar_width_spin.value(),
                'edge_width': self.edge_width_spin.value() if hasattr(self, 'edge_width_spin') else 1.0,
                'orientation': self.orientation_combo.currentText() if hasattr(self, 'orientation_combo') else "Vertical",
                'errorbar': self.errorbar_check.isChecked() if hasattr(self, 'errorbar_check') else False,
                'value_labels': self.value_labels_check.isChecked() if hasattr(self, 'value_labels_check') else False
            }
        elif self.plot_type == "hist":
            settings['hist_settings'] = {
                'bins': self.bins_spin.value(),
                'bin_method': self.bin_method_combo.currentText() if hasattr(self, 'bin_method_combo') else "auto",
                'density': self.density_check.isChecked() if hasattr(self, 'density_check') else False,
                'cumulative': self.cumulative_check.isChecked() if hasattr(self, 'cumulative_check') else False,
                'step': self.step_check.isChecked() if hasattr(self, 'step_check') else False,
                'stats': self.stats_check.isChecked() if hasattr(self, 'stats_check') else False
            }
        elif self.plot_type in ["box", "violin"]:
            settings['statistical_settings'] = {
                'outliers': self.outliers_check.isChecked() if hasattr(self, 'outliers_check') else True,
                'means': self.means_check.isChecked() if hasattr(self, 'means_check') else False,
                'notch': self.notch_check.isChecked() if hasattr(self, 'notch_check') else False,
                'box_width': self.box_width_spin.value() if hasattr(self, 'box_width_spin') else 0.8,
                'whisker': self.whisker_spin.value() if hasattr(self, 'whisker_spin') else 1.5
            }
        elif self.plot_type == "heatmap":
            settings['heatmap_settings'] = {
                'annot': self.annot_check.isChecked() if hasattr(self, 'annot_check') else True,
                'center': self.center_spin.value() if hasattr(self, 'center_spin') else 0,
                'colorbar': self.colorbar_check.isChecked() if hasattr(self, 'colorbar_check') else True,
                'square': self.square_check.isChecked() if hasattr(self, 'square_check') else False
            }
        
        # Add multi-plot settings if applicable
        if self.plot_type == "multi":
            # Get subplot configurations
            subplot_configs_data = []
            individual_styling_enabled = self.individual_styling_check.isChecked() if hasattr(self, 'individual_styling_check') else False
            
            if hasattr(self, 'subplot_configs'):
                for config in self.subplot_configs:
                    subplot_data = {
                        'plot_type': config['plot_type_combo'].currentText(),
                        'x_column': config['x_column_combo'].currentText(),
                        'y_column': config['y_column_combo'].currentText(),
                        'title': config['title_edit'].text(),
                        'xlim_min': config['xlim_min'].value(),
                        'xlim_max': config['xlim_max'].value(),
                        'ylim_min': config['ylim_min'].value(),
                        'ylim_max': config['ylim_max'].value(),
                        'individual_styling_enabled': individual_styling_enabled,
                        'axes_enabled': config['axes_group'].isEnabled()
                    }
                    subplot_configs_data.append(subplot_data)
            
            settings['multi_settings'] = {
                'grid_rows': self.grid_rows_dialog.value() if hasattr(self, 'grid_rows_dialog') else 2,
                'grid_cols': self.grid_cols_dialog.value() if hasattr(self, 'grid_cols_dialog') else 2,
                'hspace': self.hspace_spin.value() if hasattr(self, 'hspace_spin') else 0.3,
                'wspace': self.wspace_spin.value() if hasattr(self, 'wspace_spin') else 0.3,
                'individual_styling': individual_styling_enabled,
                'subplot_configs': subplot_configs_data  # Include actual subplot configurations
            }
        
        # Add enhanced axes settings
        settings['axes_settings'] = {
            'logx': self.logx_check.isChecked() if hasattr(self, 'logx_check') else False,
            'logy': self.logy_check.isChecked() if hasattr(self, 'logy_check') else False,
            'x_scale': self.x_scale_combo.currentText() if hasattr(self, 'x_scale_combo') else "linear",
            'y_scale': self.y_scale_combo.currentText() if hasattr(self, 'y_scale_combo') else "linear",
            'scientific': self.scientific_check.isChecked() if hasattr(self, 'scientific_check') else False,
            'aspect': self.aspect_combo.currentText() if hasattr(self, 'aspect_combo') else "auto",
            'x_auto_limits': self.x_auto_check.isChecked() if hasattr(self, 'x_auto_check') else True,
            'y_auto_limits': self.y_auto_check.isChecked() if hasattr(self, 'y_auto_check') else True,
            'xlim': (self.x_min_spin.value(), self.x_max_spin.value()) if hasattr(self, 'x_min_spin') else None,
            'ylim': (self.y_min_spin.value(), self.y_max_spin.value()) if hasattr(self, 'y_min_spin') else None,
            'x_tick_count': self.x_tick_count.value() if hasattr(self, 'x_tick_count') else 5,
            'y_tick_count': self.y_tick_count.value() if hasattr(self, 'y_tick_count') else 5
        }
        
        return settings
