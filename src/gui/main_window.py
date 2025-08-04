"""
Main Windfrom tabs.data_import_tab import DataImportTab
from tabs.plotting_tab import PlottingTab
from tabs.stats_tab import StatisticsTab
from tabs.signal_processing_tab import SignalProcessingTab
from core.data_manager import DataManagerr the Data Analysis GUI Application

This module contains the main window class that orchestrates all tabs
and provides the overall application structure.
"""

from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout, QWidget, 
    QMenuBar, QStatusBar, QMessageBox, QSplashScreen
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QPixmap

from .tabs.data_import_tab import DataImportTab
from .tabs.plotting_tab import PlottingTab
from .tabs.statistics_tab import StatisticsTab
from .tabs.signal_processing_tab import SignalProcessingTab
from core.data_manager import DataManager


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
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        theme_action = QAction("Toggle &Theme", self)
        theme_action.setShortcut("Ctrl+T")
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
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
        
    def new_project(self):
        """Create a new project."""
        self.data_manager.clear_data()
        self.plotting_tab.setEnabled(False)
        self.statistics_tab.setEnabled(False)
        self.signal_processing_tab.setEnabled(False)
        self.status_bar.showMessage("New project created", 2000)
        
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        # This would cycle through themes
        self.status_bar.showMessage("Theme toggled", 2000)
        
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Data Analysis Pro",
            "<h3>Data Analysis Pro v1.0.0</h3>"
            "<p>A comprehensive data analysis and visualization tool.</p>"
            "<p>Features:</p>"
            "<ul>"
            "<li>Data Import & Preview</li>"
            "<li>Interactive Plotting</li>"
            "<li>Statistical Analysis</li>"
            "<li>Signal Processing</li>"
            "</ul>"
            "<p>Built with PySide6 and Python.</p>"
        )
