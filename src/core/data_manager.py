"""
Data Manager for handling all data operations

This module provides centralized data management for the application,
including loading, processing, and sharing data between components.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
from pathlib import Path


class DataManager:
    """Centralized data management class."""
    
    def __init__(self):
        """Initialize the data manager."""
        self.data: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, Any] = {}
        self.file_path: Optional[Path] = None
        
        # Support for multiple datasets
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.current_dataset: Optional[str] = None
        
    def load_csv(self, file_path: str, **kwargs) -> bool:
        """
        Load data from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            **kwargs: Additional arguments for pandas.read_csv
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.data = pd.read_csv(file_path, **kwargs)
            self.file_path = Path(file_path)
            self._update_metadata()
            return True
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False
            
    def load_excel(self, file_path: str, sheet_name: str = 0, **kwargs) -> bool:
        """
        Load data from an Excel file.
        
        Args:
            file_path: Path to the Excel file
            sheet_name: Sheet to load (default: first sheet)
            **kwargs: Additional arguments for pandas.read_excel
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.data = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
            self.file_path = Path(file_path)
            self._update_metadata()
            return True
        except Exception as e:
            print(f"Error loading Excel: {e}")
            return False
            
    def load_text_file(self, file_path: str, separator: str = '\t', **kwargs) -> bool:
        """
        Load data from a text file (TSV, pipe-delimited, etc.).
        
        Args:
            file_path: Path to the text file
            separator: Column separator (default: tab)
            **kwargs: Additional arguments for pandas.read_csv
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove 'sep' from kwargs if it exists to avoid conflict
            if 'sep' in kwargs:
                del kwargs['sep']
            
            self.data = pd.read_csv(file_path, sep=separator, **kwargs)
            self.file_path = Path(file_path)
            self._update_metadata()
            return True
        except Exception as e:
            print(f"Error loading text file: {e}")
            return False
            
    def get_data(self) -> Optional[pd.DataFrame]:
        """Get the current dataset."""
        return self.data
        
    def has_data(self) -> bool:
        """Check if data is currently loaded."""
        return self.data is not None and not self.data.empty
        
    def get_columns(self) -> List[str]:
        """Get list of column names."""
        if self.data is not None:
            return list(self.data.columns)
        return []
        
    def get_numeric_columns(self) -> List[str]:
        """Get list of numeric column names."""
        if self.data is not None:
            return list(self.data.select_dtypes(include=[np.number]).columns)
        return []
        
    def get_analysis_columns(self) -> List[str]:
        """Get list of column names excluding sample_id for analysis."""
        if self.data is not None:
            return [col for col in self.data.columns if col != 'sample_id']
        return []
        
    def get_analysis_numeric_columns(self) -> List[str]:
        """Get list of numeric column names excluding sample_id for analysis."""
        if self.data is not None:
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns
            return [col for col in numeric_cols if col != 'sample_id']
        return []
        
    def get_categorical_columns(self) -> List[str]:
        """Get list of categorical/text column names."""
        if self.data is not None:
            return list(self.data.select_dtypes(exclude=[np.number]).columns)
        return []
        
    def get_metadata(self) -> Dict[str, Any]:
        """Get dataset metadata."""
        return self.metadata.copy()
        
    def set_data(self, data: pd.DataFrame, name: Optional[str] = None):
        """
        Set new data in the manager.
        
        Args:
            data: DataFrame to set as current data
            name: Optional name for the dataset
        """
        self.data = data.copy()
        self.file_path = None  # No file path for programmatically set data
        self._update_metadata()
        if name:
            self.metadata['name'] = name
    
    def add_data_column(self, column_name: str, data: pd.Series):
        """
        Add a new column to existing data.
        
        Args:
            column_name: Name of the new column
            data: Series data for the new column
        """
        if self.data is not None:
            self.data[column_name] = data
            self._update_metadata()
        else:
            # Create new DataFrame if no data exists
            self.data = pd.DataFrame({column_name: data})
            self._update_metadata()
        
    def clear_data(self):
        """Clear all data and reset the manager."""
        self.data = None
        self.metadata = {}
        self.file_path = None
        self.datasets = {}
        self.current_dataset = None
    
    def add_dataset(self, name: str, data: pd.DataFrame):
        """
        Add a new dataset to the collection.
        
        Args:
            name: Name for the dataset
            data: DataFrame to add
        """
        self.datasets[name] = data.copy()
        # Don't change the current main dataset
        
    def get_dataset(self, name: str) -> Optional[pd.DataFrame]:
        """
        Get a specific dataset by name.
        
        Args:
            name: Name of the dataset
            
        Returns:
            DataFrame if found, None otherwise
        """
        return self.datasets.get(name)
    
    def list_datasets(self) -> List[str]:
        """Get list of all available dataset names."""
        return list(self.datasets.keys())
    
    def switch_to_dataset(self, name: str) -> bool:
        """
        Switch the main data to a specific dataset.
        
        Args:
            name: Name of the dataset to switch to
            
        Returns:
            True if successful, False if dataset not found
        """
        if name in self.datasets:
            self.data = self.datasets[name].copy()
            self.current_dataset = name
            self._update_metadata()
            return True
        return False
        
    def _update_metadata(self):
        """Update metadata based on current data."""
        if self.data is not None:
            self.metadata = {
                'rows': len(self.data),
                'columns': len(self.data.columns),
                'missing_values': self.data.isnull().sum().sum(),
                'memory_usage': self.data.memory_usage(deep=True).sum(),
                'dtypes': dict(self.data.dtypes),
                'numeric_columns': len(self.get_numeric_columns()),
                'categorical_columns': len(self.get_categorical_columns()),
                'file_name': self.file_path.name if self.file_path else None,
                'file_size': self.file_path.stat().st_size if self.file_path and self.file_path.exists() else None
            }
            
    def get_column_stats(self, column: str) -> Dict[str, Any]:
        """
        Get basic statistics for a specific column.
        
        Args:
            column: Column name
            
        Returns:
            Dictionary with statistics
        """
        if self.data is None or column not in self.data.columns:
            return {}
            
        col_data = self.data[column]
        stats = {
            'name': column,
            'dtype': str(col_data.dtype),
            'count': col_data.count(),
            'missing': col_data.isnull().sum(),
            'unique': col_data.nunique()
        }
        
        if col_data.dtype in ['int64', 'float64', 'int32', 'float32']:
            stats.update({
                'mean': col_data.mean(),
                'median': col_data.median(),
                'std': col_data.std(),
                'min': col_data.min(),
                'max': col_data.max(),
                'variance': col_data.var()
            })
        else:
            stats.update({
                'top_value': col_data.mode().iloc[0] if not col_data.mode().empty else None,
                'top_freq': col_data.value_counts().iloc[0] if not col_data.empty else 0
            })
            
        return stats
        
    def export_data(self, file_path: str, file_format: str = 'csv') -> bool:
        """
        Export current data to file.
        
        Args:
            file_path: Output file path
            file_format: Format ('csv', 'excel', 'json')
            
        Returns:
            True if successful, False otherwise
        """
        if self.data is None:
            return False
            
        try:
            if file_format.lower() == 'csv':
                self.data.to_csv(file_path, index=False)
            elif file_format.lower() == 'excel':
                self.data.to_excel(file_path, index=False)
            elif file_format.lower() == 'json':
                self.data.to_json(file_path, orient='records', indent=2)
            else:
                return False
            return True
        except Exception as e:
            print(f"Error exporting data: {e}")
            return False
