"""
Advanced Import Settings Dialog

This module provides a dialog for configuring advanced import parameters
for different file types with presets and custom options.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QComboBox, QSpinBox, QCheckBox, QPushButton,
    QTabWidget, QWidget, QTextEdit, QMessageBox, QDialogButtonBox,
    QInputDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import json
from pathlib import Path


class ImportSettingsDialog(QDialog):
    """Dialog for configuring advanced import settings."""
    
    settings_changed = Signal(dict)
    
    def __init__(self, file_type='csv', parent=None):
        """Initialize the import settings dialog."""
        super().__init__(parent)
        self.file_type = file_type
        self.settings = {}
        self.presets = self.load_presets()
        self.setup_ui()
        self.load_default_settings()
        
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Advanced Import Settings")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Presets section
        presets_group = QGroupBox("Presets")
        presets_layout = QHBoxLayout(presets_group)
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(list(self.presets.keys()))
        self.preset_combo.currentTextChanged.connect(self.load_preset)
        
        save_preset_btn = QPushButton("Save as Preset")
        save_preset_btn.clicked.connect(self.save_preset)
        
        presets_layout.addWidget(QLabel("Load Preset:"))
        presets_layout.addWidget(self.preset_combo)
        presets_layout.addWidget(save_preset_btn)
        presets_layout.addStretch()
        
        layout.addWidget(presets_group)
        
        # Tab widget for different file types
        self.tab_widget = QTabWidget()
        
        if self.file_type in ['csv', 'txt', 'tsv']:
            self.setup_csv_tab()
        elif self.file_type in ['xlsx', 'xls']:
            self.setup_excel_tab()
            
        layout.addWidget(self.tab_widget)
        
        # Preview section
        preview_group = QGroupBox("Import Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlainText("Select a file and configure settings to see preview...")
        
        preview_layout.addWidget(self.preview_text)
        layout.addWidget(preview_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Reset
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Reset).clicked.connect(self.reset_settings)
        
        layout.addWidget(button_box)
        
    def setup_csv_tab(self):
        """Set up CSV/Text file settings tab."""
        csv_widget = QWidget()
        layout = QGridLayout(csv_widget)
        
        # Separator settings
        layout.addWidget(QLabel("Separator:"), 0, 0)
        self.separator_combo = QComboBox()
        self.separator_combo.setEditable(True)
        self.separator_combo.addItems([",", ";", "\t", "|", " ", "Custom..."])
        layout.addWidget(self.separator_combo, 0, 1)
        
        # Encoding
        layout.addWidget(QLabel("Encoding:"), 0, 2)
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(["utf-8", "latin1", "cp1252", "ascii"])
        layout.addWidget(self.encoding_combo, 0, 3)
        
        # Header settings
        layout.addWidget(QLabel("Header Row:"), 1, 0)
        self.header_combo = QComboBox()
        self.header_combo.addItems(["Auto-detect", "First row", "No header", "Custom row..."])
        layout.addWidget(self.header_combo, 1, 1)
        
        # Decimal separator
        layout.addWidget(QLabel("Decimal:"), 1, 2)
        self.decimal_combo = QComboBox()
        self.decimal_combo.setEditable(True)
        self.decimal_combo.addItems([".", ","])
        layout.addWidget(self.decimal_combo, 1, 3)
        
        # Thousands separator
        layout.addWidget(QLabel("Thousands:"), 2, 0)
        self.thousands_combo = QComboBox()
        self.thousands_combo.setEditable(True)
        self.thousands_combo.addItems(["None", ",", ".", " ", "'"])
        layout.addWidget(self.thousands_combo, 2, 1)
        
        # Skip rows
        layout.addWidget(QLabel("Skip Rows:"), 2, 2)
        self.skip_rows_spin = QSpinBox()
        self.skip_rows_spin.setMinimum(0)
        self.skip_rows_spin.setMaximum(1000)
        layout.addWidget(self.skip_rows_spin, 2, 3)
        
        # Max rows to read
        layout.addWidget(QLabel("Max Rows:"), 3, 0)
        self.max_rows_spin = QSpinBox()
        self.max_rows_spin.setMinimum(0)
        self.max_rows_spin.setMaximum(1000000)
        self.max_rows_spin.setSpecialValueText("All")
        layout.addWidget(self.max_rows_spin, 3, 1)
        
        # Date parsing
        self.parse_dates_check = QCheckBox("Auto-parse dates")
        layout.addWidget(self.parse_dates_check, 3, 2, 1, 2)
        
        # NA values
        layout.addWidget(QLabel("NA Values:"), 4, 0)
        self.na_values_edit = QLineEdit()
        self.na_values_edit.setPlaceholderText("e.g., NA,NULL,N/A,#N/A")
        layout.addWidget(self.na_values_edit, 4, 1, 1, 3)
        
        # Quote character
        layout.addWidget(QLabel("Quote Char:"), 5, 0)
        self.quote_combo = QComboBox()
        self.quote_combo.setEditable(True)
        self.quote_combo.addItems(['"', "'", "None"])
        layout.addWidget(self.quote_combo, 5, 1)
        
        # Comment character
        layout.addWidget(QLabel("Comment Char:"), 5, 2)
        self.comment_edit = QLineEdit()
        self.comment_edit.setPlaceholderText("e.g., #")
        self.comment_edit.setMaxLength(1)
        layout.addWidget(self.comment_edit, 5, 3)
        
        self.tab_widget.addTab(csv_widget, "CSV/Text Settings")
        
    def setup_excel_tab(self):
        """Set up Excel file settings tab."""
        excel_widget = QWidget()
        layout = QGridLayout(excel_widget)
        
        # Sheet selection
        layout.addWidget(QLabel("Sheet:"), 0, 0)
        self.sheet_combo = QComboBox()
        self.sheet_combo.addItems(["First sheet", "Sheet by name...", "Sheet by index..."])
        layout.addWidget(self.sheet_combo, 0, 1)
        
        # Header row
        layout.addWidget(QLabel("Header Row:"), 0, 2)
        self.excel_header_spin = QSpinBox()
        self.excel_header_spin.setMinimum(0)
        self.excel_header_spin.setMaximum(100)
        layout.addWidget(self.excel_header_spin, 0, 3)
        
        # Skip rows
        layout.addWidget(QLabel("Skip Rows:"), 1, 0)
        self.excel_skip_spin = QSpinBox()
        self.excel_skip_spin.setMinimum(0)
        self.excel_skip_spin.setMaximum(1000)
        layout.addWidget(self.excel_skip_spin, 1, 1)
        
        # Max rows
        layout.addWidget(QLabel("Max Rows:"), 1, 2)
        self.excel_max_rows_spin = QSpinBox()
        self.excel_max_rows_spin.setMinimum(0)
        self.excel_max_rows_spin.setMaximum(1000000)
        self.excel_max_rows_spin.setSpecialValueText("All")
        layout.addWidget(self.excel_max_rows_spin, 1, 3)
        
        # Date parsing
        self.excel_parse_dates_check = QCheckBox("Auto-parse dates")
        layout.addWidget(self.excel_parse_dates_check, 2, 0, 1, 2)
        
        # NA values
        layout.addWidget(QLabel("NA Values:"), 3, 0)
        self.excel_na_values_edit = QLineEdit()
        self.excel_na_values_edit.setPlaceholderText("e.g., NA,NULL,N/A")
        layout.addWidget(self.excel_na_values_edit, 3, 1, 1, 3)
        
        self.tab_widget.addTab(excel_widget, "Excel Settings")
        
    def load_presets(self):
        """Load predefined presets."""
        return {
            "Default CSV": {
                "separator": ",",
                "encoding": "utf-8",
                "header": "infer",
                "decimal": ".",
                "thousands": None,
                "parse_dates": False
            },
            "European CSV": {
                "separator": ";",
                "encoding": "utf-8", 
                "header": "infer",
                "decimal": ",",
                "thousands": ".",
                "parse_dates": False
            },
            "Tab Separated": {
                "separator": "\t",
                "encoding": "utf-8",
                "header": "infer", 
                "decimal": ".",
                "thousands": ",",
                "parse_dates": False
            },
            "Pipe Delimited": {
                "separator": "|",
                "encoding": "utf-8",
                "header": "infer",
                "decimal": ".",
                "thousands": None,
                "parse_dates": False
            },
            "No Header CSV": {
                "separator": ",",
                "encoding": "utf-8",
                "header": None,
                "decimal": ".",
                "thousands": None,
                "parse_dates": False
            }
        }
        
    def load_preset(self, preset_name):
        """Load settings from a preset."""
        if preset_name in self.presets:
            settings = self.presets[preset_name]
            self.apply_settings(settings)
            
    def apply_settings(self, settings):
        """Apply settings to the UI controls."""
        if self.file_type in ['csv', 'txt', 'tsv']:
            # CSV settings
            if "separator" in settings:
                sep = settings["separator"]
                if sep == "\t":
                    self.separator_combo.setCurrentText("\t")
                else:
                    self.separator_combo.setCurrentText(sep)
                    
            if "encoding" in settings:
                self.encoding_combo.setCurrentText(settings["encoding"])
                
            if "decimal" in settings:
                self.decimal_combo.setCurrentText(settings["decimal"])
                
            if "parse_dates" in settings:
                self.parse_dates_check.setChecked(settings["parse_dates"])
                
    def get_settings(self):
        """Get current settings as a dictionary."""
        settings = {}
        
        if self.file_type in ['csv', 'txt', 'tsv']:
            # CSV/Text settings
            sep = self.separator_combo.currentText()
            if sep == "\t":
                settings["sep"] = "\t"
            else:
                settings["sep"] = sep
                
            settings["encoding"] = self.encoding_combo.currentText()
            settings["decimal"] = self.decimal_combo.currentText()
            
            # Header handling
            header_text = self.header_combo.currentText()
            if header_text == "Auto-detect":
                settings["header"] = "infer"
            elif header_text == "First row":
                settings["header"] = 0
            elif header_text == "No header":
                settings["header"] = None
                
            # Skip rows
            if self.skip_rows_spin.value() > 0:
                settings["skiprows"] = self.skip_rows_spin.value()
                
            # Max rows
            if self.max_rows_spin.value() > 0:
                settings["nrows"] = self.max_rows_spin.value()
                
            # Parse dates
            settings["parse_dates"] = self.parse_dates_check.isChecked()
            
            # NA values
            na_text = self.na_values_edit.text().strip()
            if na_text:
                settings["na_values"] = [val.strip() for val in na_text.split(",")]
                
            # Thousands separator
            thousands = self.thousands_combo.currentText()
            if thousands != "None":
                settings["thousands"] = thousands
                
            # Quote character
            quote = self.quote_combo.currentText()
            if quote != "None":
                settings["quotechar"] = quote
                
            # Comment character
            comment = self.comment_edit.text().strip()
            if comment:
                settings["comment"] = comment
                
        elif self.file_type in ['xlsx', 'xls']:
            # Excel settings
            if self.excel_skip_spin.value() > 0:
                settings["skiprows"] = self.excel_skip_spin.value()
                
            if self.excel_max_rows_spin.value() > 0:
                settings["nrows"] = self.excel_max_rows_spin.value()
                
            settings["header"] = self.excel_header_spin.value()
            settings["parse_dates"] = self.excel_parse_dates_check.isChecked()
            
            # NA values
            na_text = self.excel_na_values_edit.text().strip()
            if na_text:
                settings["na_values"] = [val.strip() for val in na_text.split(",")]
                
        return settings
        
    def save_preset(self):
        """Save current settings as a new preset."""
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if ok and name:
            self.presets[name] = self.get_settings()
            self.preset_combo.addItem(name)
            self.preset_combo.setCurrentText(name)
            
    def reset_settings(self):
        """Reset settings to defaults."""
        self.load_default_settings()
        
    def load_default_settings(self):
        """Load default settings."""
        if "Default CSV" in self.presets:
            self.apply_settings(self.presets["Default CSV"])
            
    def accept(self):
        """Accept dialog and emit settings."""
        settings = self.get_settings()
        self.settings_changed.emit(settings)
        super().accept()
