"""
Data Import and Preview Tab

This module provides the interface for loading data files and
previewing their contents with metadata information.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QLabel, QGroupBox, QFileDialog, QMessageBox,
    QProgressBar, QTextEdit, QSplitter, QFrame, QGridLayout, QComboBox,
    QCheckBox, QInputDialog
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont
import pandas as pd
from pathlib import Path
from ..dialogs.import_settings_dialog import ImportSettingsDialog


class DataImportTab(QWidget):
    """Tab for importing and previewing data."""
    
    data_loaded = Signal()
    
    def __init__(self, data_manager):
        """Initialize the data import tab."""
        super().__init__()
        self.data_manager = data_manager
        self.last_file_path = None
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Import section
        import_group = QGroupBox("Data Import")
        import_layout = QVBoxLayout(import_group)
        
        # File selection row
        file_row = QHBoxLayout()
        
        self.load_button = QPushButton("📂 Load Data File")
        self.load_button.setMinimumHeight(40)
        self.load_button.clicked.connect(self.load_data)
        
        self.advanced_button = QPushButton("⚙️ Advanced Settings")
        self.advanced_button.setMinimumHeight(40)
        self.advanced_button.clicked.connect(self.show_advanced_settings)
        
        file_row.addWidget(self.load_button)
        file_row.addWidget(self.advanced_button)
        file_row.addStretch()
        
        # File info row
        info_row = QHBoxLayout()
        
        self.file_path_label = QLabel("No file loaded")
        self.file_path_label.setStyleSheet("color: #666; font-style: italic;")
        
        # Quick preset selection
        preset_label = QLabel("Quick Preset:")
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Auto-detect", "Default CSV", "European CSV (;)", 
            "Tab Separated", "Pipe Delimited", "Excel", "Custom"
        ])
        self.preset_combo.currentTextChanged.connect(self.preset_changed)
        
        info_row.addWidget(self.file_path_label, 1)
        info_row.addWidget(preset_label)
        info_row.addWidget(self.preset_combo)
        
        import_layout.addLayout(file_row)
        import_layout.addLayout(info_row)
        
        layout.addWidget(import_group)
        
        # Store custom import settings
        self.custom_settings = {}
        
        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Data preview
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Data preview group
        preview_group = QGroupBox("Data Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        # Table for data preview
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        preview_layout.addWidget(self.data_table)
        
        left_layout.addWidget(preview_group)
        
        # Right side - Metadata and statistics
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Metadata group
        metadata_group = QGroupBox("Dataset Information")
        metadata_layout = QGridLayout(metadata_group)
        
        # Basic info labels
        self.rows_label = QLabel("Rows: -")
        self.columns_label = QLabel("Columns: -")
        self.missing_label = QLabel("Missing Values: -")
        self.memory_label = QLabel("Memory Usage: -")
        self.file_size_label = QLabel("File Size: -")
        
        metadata_layout.addWidget(QLabel("📊 Basic Statistics"), 0, 0, 1, 2)
        metadata_layout.addWidget(self.rows_label, 1, 0)
        metadata_layout.addWidget(self.columns_label, 1, 1)
        metadata_layout.addWidget(self.missing_label, 2, 0)
        metadata_layout.addWidget(self.memory_label, 2, 1)
        metadata_layout.addWidget(self.file_size_label, 3, 0, 1, 2)
        
        right_layout.addWidget(metadata_group)
        
        # Column info group
        column_group = QGroupBox("Column Information")
        column_layout = QVBoxLayout(column_group)
        
        self.column_info_text = QTextEdit()
        self.column_info_text.setMaximumHeight(200)
        self.column_info_text.setReadOnly(True)
        column_layout.addWidget(self.column_info_text)
        
        right_layout.addWidget(column_group)
        
        # Data types group
        types_group = QGroupBox("Data Types Summary")
        types_layout = QVBoxLayout(types_group)
        
        self.types_text = QTextEdit()
        self.types_text.setMaximumHeight(150)
        self.types_text.setReadOnly(True)
        types_layout.addWidget(self.types_text)
        
        right_layout.addWidget(types_group)
        
        # Add stretch to push everything up
        right_layout.addStretch()
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([700, 300])  # 70% preview, 30% info
        
        layout.addWidget(splitter)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
    def load_data(self):
        """Load data from a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Data File",
            "",
            "All Supported (*.csv *.txt *.tsv *.xlsx *.xls);;CSV Files (*.csv);;Text Files (*.txt *.tsv);;Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        
        if file_path:
            self.last_file_path = file_path
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            success = False
            file_ext = Path(file_path).suffix.lower()
            
            # Get settings based on preset or custom settings
            load_settings = self.get_current_settings(file_ext)
            
            try:
                if file_ext == '.csv':
                    success = self.data_manager.load_csv(file_path, **load_settings)
                elif file_ext in ['.txt', '.tsv']:
                    success = self.data_manager.load_text_file(file_path, **load_settings)
                elif file_ext in ['.xlsx', '.xls']:
                    success = self.data_manager.load_excel(file_path, **load_settings)
                else:
                    # Try to auto-detect format
                    if self.try_auto_detect(file_path, load_settings):
                        success = True
                    else:
                        QMessageBox.warning(self, "Unsupported Format", 
                                          f"File format {file_ext} is not supported.")
                    
                if success:
                    self.file_path_label.setText(f"Loaded: {Path(file_path).name}")
                    self.file_path_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
                    self.update_preview()
                    self.data_loaded.emit()
                else:
                    QMessageBox.critical(self, "Error", "Failed to load the data file.")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading file: {str(e)}")
                
            finally:
                self.progress_bar.setVisible(False)
                
    def try_auto_detect(self, file_path, base_settings):
        """Try to auto-detect file format and load."""
        # Try common separators
        separators = [',', ';', '\t', '|']
        
        for sep in separators:
            try:
                settings = base_settings.copy()
                settings['sep'] = sep
                if self.data_manager.load_csv(file_path, **settings):
                    return True
            except:
                continue
                
        return False
        
    def get_current_settings(self, file_ext):
        """Get current import settings based on preset and file type."""
        preset = self.preset_combo.currentText()
        
        # Base settings from preset
        if preset == "Auto-detect":
            settings = {}
        elif preset == "Default CSV":
            settings = {"sep": ",", "encoding": "utf-8"}
        elif preset == "European CSV (;)":
            settings = {"sep": ";", "encoding": "utf-8", "decimal": ","}
        elif preset == "Tab Separated":
            settings = {"sep": "\t", "encoding": "utf-8"}
        elif preset == "Pipe Delimited":
            settings = {"sep": "|", "encoding": "utf-8"}
        elif preset == "Excel":
            settings = {"sheet_name": 0}
        else:
            settings = {}
            
        # Override with custom settings if available
        if self.custom_settings:
            settings.update(self.custom_settings)
            
        return settings
        
    def show_advanced_settings(self):
        """Show the advanced import settings dialog."""
        # Determine file type from current selection or last loaded file
        file_type = 'csv'  # default
        
        if hasattr(self, 'last_file_path') and self.last_file_path:
            ext = Path(self.last_file_path).suffix.lower()
            if ext in ['.xlsx', '.xls']:
                file_type = 'xlsx'
            elif ext in ['.txt', '.tsv']:
                file_type = 'txt'
                
        dialog = ImportSettingsDialog(file_type, self)
        dialog.settings_changed.connect(self.on_custom_settings_changed)
        
        if dialog.exec():
            self.custom_settings = dialog.get_settings()
            self.preset_combo.setCurrentText("Custom")
            
    def on_custom_settings_changed(self, settings):
        """Handle custom settings change."""
        self.custom_settings = settings
        
    def preset_changed(self, preset_name):
        """Handle preset change."""
        if preset_name != "Custom":
            self.custom_settings = {}
                
    def update_preview(self):
        """Update the data preview and metadata."""
        data = self.data_manager.get_data()
        if data is None:
            return
            
        # Update table with first 100 rows
        preview_data = data.head(100)
        self.data_table.setRowCount(len(preview_data))
        self.data_table.setColumnCount(len(preview_data.columns))
        self.data_table.setHorizontalHeaderLabels([str(col) for col in preview_data.columns])
        
        # Populate table
        for i, row in enumerate(preview_data.itertuples(index=False)):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.data_table.setItem(i, j, item)
                
        # Resize columns to content
        self.data_table.resizeColumnsToContents()
        
        # Update metadata
        metadata = self.data_manager.get_metadata()
        self.rows_label.setText(f"Rows: {metadata.get('rows', 0):,}")
        self.columns_label.setText(f"Columns: {metadata.get('columns', 0)}")
        self.missing_label.setText(f"Missing Values: {metadata.get('missing_values', 0):,}")
        
        # Format memory usage
        memory_mb = metadata.get('memory_usage', 0) / (1024 * 1024)
        self.memory_label.setText(f"Memory: {memory_mb:.2f} MB")
        
        # Format file size
        file_size = metadata.get('file_size', 0)
        if file_size:
            file_size_mb = file_size / (1024 * 1024)
            self.file_size_label.setText(f"File Size: {file_size_mb:.2f} MB")
        
        # Update column information
        self.update_column_info()
        
        # Update data types summary
        self.update_types_summary()
        
    def update_column_info(self):
        """Update column information display."""
        columns = self.data_manager.get_columns()
        numeric_cols = self.data_manager.get_numeric_columns()
        categorical_cols = self.data_manager.get_categorical_columns()
        
        info_text = f"Total Columns: {len(columns)}\n"
        info_text += f"Numeric: {len(numeric_cols)}\n"
        info_text += f"Categorical: {len(categorical_cols)}\n\n"
        
        info_text += "Numeric Columns:\n"
        for col in numeric_cols[:10]:  # Show first 10
            info_text += f"  • {col}\n"
        if len(numeric_cols) > 10:
            info_text += f"  ... and {len(numeric_cols) - 10} more\n"
            
        info_text += "\nCategorical Columns:\n"
        for col in categorical_cols[:10]:  # Show first 10
            info_text += f"  • {col}\n"
        if len(categorical_cols) > 10:
            info_text += f"  ... and {len(categorical_cols) - 10} more\n"
            
        self.column_info_text.setPlainText(info_text)
        
    def update_types_summary(self):
        """Update data types summary."""
        metadata = self.data_manager.get_metadata()
        dtypes = metadata.get('dtypes', {})
        
        # Count data types
        type_counts = {}
        for dtype in dtypes.values():
            dtype_str = str(dtype)
            type_counts[dtype_str] = type_counts.get(dtype_str, 0) + 1
            
        types_text = "Data Type Distribution:\n\n"
        for dtype, count in sorted(type_counts.items()):
            types_text += f"{dtype}: {count} columns\n"
            
        self.types_text.setPlainText(types_text)
