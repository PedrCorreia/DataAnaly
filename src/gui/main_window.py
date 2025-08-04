"""
Main Window for the Data Analysis GUI Application

This module contains the main window class that orchestrates all tabs
and provides the overall application structure.
"""

from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout, QWidget, 
    QMenuBar, QStatusBar, QMessageBox, QSplashScreen, QApplication,
    QDialog, QLabel, QListWidget, QListWidgetItem, QHBoxLayout, QPushButton
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QPixmap

from .tabs.data_import_tab import DataImportTab
from .tabs.plotting_tab import PlottingTab
from .tabs.statistics_tab import StatisticsTab
from .tabs.signal_processing_tab import SignalProcessingTab
from ..core.data_manager import DataManager


class MainWindow(QMainWindow):
    """Main application window with tabbed interface."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.data_manager = DataManager()
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        
    def setup_ui(self):
        """Set up the main user interface."""
        self.setWindowTitle("Data Analysis Pro")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setDocumentMode(True)
        
        # Create and add tabs
        self.data_import_tab = DataImportTab(self.data_manager)
        self.plotting_tab = PlottingTab(self.data_manager)
        self.statistics_tab = StatisticsTab(self.data_manager)
        self.signal_processing_tab = SignalProcessingTab(self.data_manager)
        
        self.tab_widget.addTab(self.data_import_tab, "📊 Data Import & Preview")
        self.tab_widget.addTab(self.plotting_tab, "📈 Plotting")
        self.tab_widget.addTab(self.statistics_tab, "📋 Statistical Analysis")
        self.tab_widget.addTab(self.signal_processing_tab, "🔬 Signal Processing")
        
        # Connect data updates
        self.data_import_tab.data_loaded.connect(self.on_data_loaded)
        
        # Connect statistics tab data creation
        self.statistics_tab.data_created.connect(self.on_data_created)
        
        layout.addWidget(self.tab_widget)
        
    def setup_menu(self):
        """Set up the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open Data...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.data_import_tab.load_data)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Dataset management
        switch_dataset_action = QAction("&Switch Dataset...", self)
        switch_dataset_action.setShortcut("Ctrl+Shift+S")
        switch_dataset_action.triggered.connect(self.switch_dataset_dialog)
        file_menu.addAction(switch_dataset_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        user_guide_action = QAction("&User Guide", self)
        user_guide_action.setShortcut("F1")
        user_guide_action.triggered.connect(self.show_user_guide)
        help_menu.addAction(user_guide_action)
        
        shortcuts_action = QAction("Keyboard &Shortcuts", self)
        shortcuts_action.setShortcut("Ctrl+?")
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_status_bar(self):
        """Set up the status bar."""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
    def on_data_loaded(self):
        """Handle data loading completion."""
        self.status_bar.showMessage("Data loaded successfully", 3000)
        
        # Enable other tabs
        self.plotting_tab.setEnabled(True)
        self.statistics_tab.setEnabled(True)
        self.signal_processing_tab.setEnabled(True)
        
        # Update other tabs with new data
        self.plotting_tab.update_column_lists()
        self.statistics_tab.update_column_lists()
        self.signal_processing_tab.update_column_lists()
        
    def on_data_created(self, name, dataframe):
        """Handle creation of new data from statistics/signal processing."""
        try:
            # Add the new dataset to the collection without replacing the main data
            self.data_manager.add_dataset(name, dataframe)
            
            self.status_bar.showMessage(f"New dataset created: {name} (original data preserved)", 3000)
            
            # Show information about the new dataset
            QMessageBox.information(self, "Dataset Created", 
                f"New dataset '{name}' has been created with {len(dataframe)} rows and {len(dataframe.columns)} columns.\n\n"
                f"The original data remains active. Use File > Switch Dataset to view the new dataset.")
            
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not add dataset: {str(e)}")
        
    def new_project(self):
        """Create a new project."""
        self.data_manager.clear_data()
        self.plotting_tab.setEnabled(False)
        self.statistics_tab.setEnabled(False)
        self.signal_processing_tab.setEnabled(False)
        self.status_bar.showMessage("New project created", 2000)
    
    def switch_dataset_dialog(self):
        """Show dialog to switch between available datasets."""
        datasets = self.data_manager.list_datasets()
        
        if not datasets:
            QMessageBox.information(self, "No Datasets", 
                "No additional datasets available. Create datasets using Statistics or Signal Processing tabs.")
            return
        
        # Add the original dataset option
        current_data_name = "Original Data"
        all_options = [current_data_name] + datasets
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Switch Dataset")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        
        # Instructions
        label = QLabel("Select a dataset to view:")
        layout.addWidget(label)
        
        # Dataset list
        dataset_list = QListWidget()
        for option in all_options:
            item = QListWidgetItem(option)
            if option == current_data_name:
                item.setText(f"{option} (Current)")
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            dataset_list.addItem(item)
        layout.addWidget(dataset_list)
        
        # Info label
        info_label = QLabel("Click a dataset to see details")
        layout.addWidget(info_label)
        
        # Update info when selection changes
        def update_info():
            current_item = dataset_list.currentItem()
            if current_item:
                dataset_name = current_item.text().replace(" (Current)", "")
                if dataset_name == current_data_name:
                    data = self.data_manager.get_data()
                else:
                    data = self.data_manager.get_dataset(dataset_name)
                
                if data is not None:
                    info_text = f"Rows: {len(data)}, Columns: {len(data.columns)}"
                    info_label.setText(info_text)
        
        dataset_list.currentItemChanged.connect(update_info)
        
        # Buttons
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        switch_btn = QPushButton("Switch")
        switch_btn.clicked.connect(dialog.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(switch_btn)
        layout.addLayout(button_layout)
        
        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            current_item = dataset_list.currentItem()
            if current_item:
                selected_name = current_item.text().replace(" (Current)", "")
                
                if selected_name != current_data_name:
                    # Switch to selected dataset
                    if self.data_manager.switch_to_dataset(selected_name):
                        self.status_bar.showMessage(f"Switched to dataset: {selected_name}", 3000)
                        
                        # Update all tabs
                        self.plotting_tab.update_column_lists()
                        self.statistics_tab.update_column_lists()
                        self.signal_processing_tab.update_column_lists()
                    else:
                        QMessageBox.warning(self, "Error", f"Could not switch to dataset: {selected_name}")
                else:
                    # User selected original data - no action needed
                    pass
        
    def show_about(self):
        """Show enhanced about dialog."""
        about_text = """
        <div style='text-align: center;'>
        <h2>🚀 Data Analysis Pro</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Build Date:</b> August 2025</p>
        </div>
        
        <h3>📊 Professional Data Analysis & Visualization</h3>
        <p>A comprehensive, modern data analysis application built with PySide6.</p>
        
        <h4>✨ Key Features:</h4>
        <ul>
        <li><b>📈 Data Import & Preview</b> - Load CSV, Excel, and text files with intelligent detection</li>
        <li><b>🎨 Interactive Plotting</b> - Professional charts with scientific formatting and export</li>
        <li><b>📋 Statistical Analysis</b> - Descriptive stats, hypothesis testing, and correlations</li>
        <li><b>🔬 Signal Processing</b> - Digital filtering, FFT analysis, and frequency domain plots</li>
        </ul>
        
        <h4>🛠️ Technical Stack:</h4>
        <p><b>GUI Framework:</b> PySide6 (Qt for Python)<br>
        <b>Data Processing:</b> Pandas, NumPy<br>
        <b>Visualization:</b> Matplotlib, Seaborn<br>
        <b>Signal Processing:</b> SciPy<br>
        <b>Language:</b> Python 3.10+</p>
        
        <h4>💡 Why PySide6?</h4>
        <p>Unlike tkinter, PySide6 provides:</p>
        <ul>
        <li>Native OS look and feel</li>
        <li>Professional styling and theming</li>
        <li>High DPI display support</li>
        <li>Better performance with large datasets</li>
        <li>Advanced widgets and layouts</li>
        </ul>
        
        <p style='text-align: center; margin-top: 20px;'>
        <b>Built for data scientists, by data scientists</b><br>
        <small>© 2025 Data Analysis Pro</small>
        </p>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About Data Analysis Pro")
        msg_box.setText(about_text)
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()
        
    def show_user_guide(self):
        """Show user guide dialog."""
        guide_text = """
        <h2>📖 Quick Start Guide</h2>
        
        <h3>🚀 Getting Started</h3>
        <ol>
        <li><b>Import Data:</b> Use the "📊 Data Import & Preview" tab to load your data files</li>
        <li><b>Explore:</b> Review the data preview and metadata</li>
        <li><b>Visualize:</b> Switch to "📈 Plotting" tab for interactive charts</li>
        <li><b>Analyze:</b> Use "📋 Statistical Analysis" for descriptive stats and tests</li>
        <li><b>Process:</b> Apply signal processing in the "🔬 Signal Processing" tab</li>
        </ol>
        
        <h3>📂 Data Import Features</h3>
        <ul>
        <li><b>Quick Presets:</b> Default CSV, European CSV, Tab/Pipe delimited, Excel</li>
        <li><b>Advanced Settings:</b> Custom separators, encoding, headers, etc.</li>
        <li><b>File Types:</b> CSV, TXT, TSV, XLS, XLSX</li>
        <li><b>Dynamic Reload:</b> Switch presets and reload instantly</li>
        </ul>
        
        <h3>📈 Plotting Capabilities</h3>
        <ul>
        <li><b>Plot Types:</b> Line, Scatter, Bar, Histogram, Box, Violin, Heatmap, Pair plots</li>
        <li><b>Customization:</b> Colors, styles, fonts, transparency, scientific notation</li>
        <li><b>Export Formats:</b> PNG, PDF, SVG, JPG, LaTeX (TikZ)</li>
        <li><b>Interactive:</b> Real-time preview with zoom, pan, and navigation</li>
        </ul>
        
        <h3>⌨️ Keyboard Shortcuts</h3>
        <ul>
        <li><b>Ctrl+N:</b> New Project</li>
        <li><b>Ctrl+O:</b> Open Data File</li>
        <li><b>Ctrl+Q:</b> Exit Application</li>
        <li><b>F1:</b> Show User Guide</li>
        <li><b>Ctrl+?:</b> Show Keyboard Shortcuts</li>
        </ul>
        
        <h3>💡 Pro Tips</h3>
        <ul>
        <li>Use the reload button (🔄) to quickly test different import presets</li>
        <li>Adjust DPI settings in plotting for publication-quality exports</li>
        <li>Use scientific notation and log scales for research data</li>
        <li>Save custom color palettes for consistent styling</li>
        </ul>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("User Guide - Data Analysis Pro")
        msg_box.setText(guide_text)
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()
        
    def show_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        shortcuts_text = """
        <h2>⌨️ Keyboard Shortcuts</h2>
        
        <h3>🗂️ File Operations</h3>
        <table style='width: 100%;'>
        <tr><td><b>Ctrl+N</b></td><td>New Project</td></tr>
        <tr><td><b>Ctrl+O</b></td><td>Open Data File</td></tr>
        <tr><td><b>Ctrl+S</b></td><td>Save Project</td></tr>
        <tr><td><b>Ctrl+Q</b></td><td>Exit Application</td></tr>
        </table>
        
        <h3>🎨 View & Interface</h3>
        <table style='width: 100%;'>
        <tr><td><b>Ctrl+1</b></td><td>Switch to Data Import Tab</td></tr>
        <tr><td><b>Ctrl+2</b></td><td>Switch to Plotting Tab</td></tr>
        <tr><td><b>Ctrl+3</b></td><td>Switch to Statistics Tab</td></tr>
        <tr><td><b>Ctrl+4</b></td><td>Switch to Signal Processing Tab</td></tr>
        </table>
        
        <h3>📈 Plotting</h3>
        <table style='width: 100%;'>
        <tr><td><b>Ctrl+E</b></td><td>Export Current Plot</td></tr>
        <tr><td><b>Ctrl+C</b></td><td>Copy Plot to Clipboard</td></tr>
        <tr><td><b>Ctrl+R</b></td><td>Reset Plot View</td></tr>
        </table>
        
        <h3>❓ Help & Information</h3>
        <table style='width: 100%;'>
        <tr><td><b>F1</b></td><td>Show User Guide</td></tr>
        <tr><td><b>Ctrl+?</b></td><td>Show Keyboard Shortcuts</td></tr>
        <tr><td><b>Ctrl+I</b></td><td>Show About Dialog</td></tr>
        </table>
        
        <h3>🔧 Data Operations</h3>
        <table style='width: 100%;'>
        <tr><td><b>F5</b></td><td>Refresh/Reload Data</td></tr>
        <tr><td><b>Ctrl+F</b></td><td>Find in Data</td></tr>
        <tr><td><b>Ctrl+D</b></td><td>Show Data Info</td></tr>
        </table>
        
        <p style='margin-top: 20px;'><i>Note: Some shortcuts may vary based on the active tab and context.</i></p>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Keyboard Shortcuts - Data Analysis Pro")
        msg_box.setText(shortcuts_text)
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()
