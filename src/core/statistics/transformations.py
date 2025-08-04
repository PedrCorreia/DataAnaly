"""
Data Transformations Module

Provides data transformation capabilities for statistical analysis.
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from typing import Dict, List, Any, Optional, Tuple


class DataTransformations:
    """Handles various data transformation operations."""
    
    def __init__(self):
        self.available_transformations = {
            'log': self.log_transform,
            'sqrt': self.sqrt_transform,
            'square': self.square_transform,
            'reciprocal': self.reciprocal_transform,
            'box_cox': self.box_cox_transform,
            'standardize': self.standardize_transform,
            'normalize': self.normalize_transform,
            'robust_scale': self.robust_scale_transform,
            'rank': self.rank_transform,
            'zscore': self.zscore_transform
        }
    
    def log_transform(self, data: pd.Series, base: str = 'natural') -> Dict[str, Any]:
        """
        Apply logarithmic transformation.
        
        Args:
            data: Input data series
            base: Type of logarithm ('natural', '10', '2')
            
        Returns:
            Dictionary containing transformed data and metadata
        """
        # Ensure positive values
        min_val = data.min()
        if min_val <= 0:
            # Shift data to be positive
            shifted_data = data - min_val + 1
            shift_applied = True
            shift_value = -min_val + 1
        else:
            shifted_data = data
            shift_applied = False
            shift_value = 0
        
        # Apply transformation
        if base == 'natural':
            transformed = np.log(shifted_data)
            transform_name = 'Natural Log'
        elif base == '10':
            transformed = np.log10(shifted_data)
            transform_name = 'Log Base 10'
        elif base == '2':
            transformed = np.log2(shifted_data)
            transform_name = 'Log Base 2'
        else:
            raise ValueError("Base must be 'natural', '10', or '2'")
        
        return {
            'transformed_data': transformed,
            'transform_type': transform_name,
            'base': base,
            'shift_applied': shift_applied,
            'shift_value': shift_value,
            'original_min': min_val,
            'metadata': {
                'method': f'log_{base}',
                'parameters': {'base': base, 'shift': shift_value}
            }
        }
    
    def sqrt_transform(self, data: pd.Series) -> Dict[str, Any]:
        """
        Apply square root transformation.
        
        Args:
            data: Input data series
            
        Returns:
            Dictionary containing transformed data and metadata
        """
        # Ensure non-negative values
        min_val = data.min()
        if min_val < 0:
            # Shift data to be non-negative
            shifted_data = data - min_val
            shift_applied = True
            shift_value = -min_val
        else:
            shifted_data = data
            shift_applied = False
            shift_value = 0
        
        transformed = np.sqrt(shifted_data)
        
        return {
            'transformed_data': transformed,
            'transform_type': 'Square Root',
            'shift_applied': shift_applied,
            'shift_value': shift_value,
            'original_min': min_val,
            'metadata': {
                'method': 'sqrt',
                'parameters': {'shift': shift_value}
            }
        }
    
    def square_transform(self, data: pd.Series) -> Dict[str, Any]:
        """
        Apply square transformation.
        
        Args:
            data: Input data series
            
        Returns:
            Dictionary containing transformed data and metadata
        """
        transformed = np.square(data)
        
        return {
            'transformed_data': transformed,
            'transform_type': 'Square',
            'shift_applied': False,
            'shift_value': 0,
            'metadata': {
                'method': 'square',
                'parameters': {}
            }
        }
    
    def reciprocal_transform(self, data: pd.Series) -> Dict[str, Any]:
        """
        Apply reciprocal transformation.
        
        Args:
            data: Input data series
            
        Returns:
            Dictionary containing transformed data and metadata
        """
        # Handle zero values
        if (data == 0).any():
            # Add small constant to avoid division by zero
            epsilon = 1e-10
            shifted_data = data + epsilon
            shift_applied = True
            shift_value = epsilon
        else:
            shifted_data = data
            shift_applied = False
            shift_value = 0
        
        transformed = 1 / shifted_data
        
        return {
            'transformed_data': transformed,
            'transform_type': 'Reciprocal',
            'shift_applied': shift_applied,
            'shift_value': shift_value,
            'metadata': {
                'method': 'reciprocal',
                'parameters': {'epsilon': shift_value}
            }
        }
    
    def box_cox_transform(self, data: pd.Series) -> Dict[str, Any]:
        """
        Apply Box-Cox transformation.
        
        Args:
            data: Input data series
            
        Returns:
            Dictionary containing transformed data and metadata
        """
        # Ensure positive values
        min_val = data.min()
        if min_val <= 0:
            # Shift data to be positive
            shifted_data = data - min_val + 1
            shift_applied = True
            shift_value = -min_val + 1
        else:
            shifted_data = data
            shift_applied = False
            shift_value = 0
        
        try:
            transformed, lambda_param = stats.boxcox(shifted_data.dropna())
            transformed = pd.Series(transformed, index=shifted_data.dropna().index)
        except Exception as e:
            raise ValueError(f"Box-Cox transformation failed: {str(e)}")
        
        return {
            'transformed_data': transformed,
            'transform_type': f'Box-Cox (λ={lambda_param:.4f})',
            'lambda': lambda_param,
            'shift_applied': shift_applied,
            'shift_value': shift_value,
            'original_min': min_val,
            'metadata': {
                'method': 'box_cox',
                'parameters': {'lambda': lambda_param, 'shift': shift_value}
            }
        }
    
    def standardize_transform(self, data: pd.Series) -> Dict[str, Any]:
        """
        Apply standardization (z-score normalization).
        
        Args:
            data: Input data series
            
        Returns:
            Dictionary containing transformed data and metadata
        """
        scaler = StandardScaler()
        transformed = scaler.fit_transform(data.values.reshape(-1, 1)).flatten()
        transformed = pd.Series(transformed, index=data.index)
        
        return {
            'transformed_data': transformed,
            'transform_type': 'Standardization (Z-score)',
            'mean': scaler.mean_[0],
            'std': scaler.scale_[0],
            'scaler': scaler,
            'metadata': {
                'method': 'standardize',
                'parameters': {'mean': scaler.mean_[0], 'std': scaler.scale_[0]}
            }
        }
    
    def normalize_transform(self, data: pd.Series) -> Dict[str, Any]:
        """
        Apply min-max normalization.
        
        Args:
            data: Input data series
            
        Returns:
            Dictionary containing transformed data and metadata
        """
        scaler = MinMaxScaler()
        transformed = scaler.fit_transform(data.values.reshape(-1, 1)).flatten()
        transformed = pd.Series(transformed, index=data.index)
        
        return {
            'transformed_data': transformed,
            'transform_type': 'Min-Max Normalization',
            'min': scaler.data_min_[0],
            'max': scaler.data_max_[0],
            'range': scaler.data_range_[0],
            'scaler': scaler,
            'metadata': {
                'method': 'normalize',
                'parameters': {'min': scaler.data_min_[0], 'max': scaler.data_max_[0]}
            }
        }
    
    def robust_scale_transform(self, data: pd.Series) -> Dict[str, Any]:
        """
        Apply robust scaling (using median and IQR).
        
        Args:
            data: Input data series
            
        Returns:
            Dictionary containing transformed data and metadata
        """
        scaler = RobustScaler()
        transformed = scaler.fit_transform(data.values.reshape(-1, 1)).flatten()
        transformed = pd.Series(transformed, index=data.index)
        
        return {
            'transformed_data': transformed,
            'transform_type': 'Robust Scaling',
            'center': scaler.center_[0],
            'scale': scaler.scale_[0],
            'scaler': scaler,
            'metadata': {
                'method': 'robust_scale',
                'parameters': {'center': scaler.center_[0], 'scale': scaler.scale_[0]}
            }
        }
    
    def rank_transform(self, data: pd.Series, method: str = 'average') -> Dict[str, Any]:
        """
        Apply rank transformation.
        
        Args:
            data: Input data series
            method: Ranking method ('average', 'min', 'max', 'first', 'dense')
            
        Returns:
            Dictionary containing transformed data and metadata
        """
        transformed = data.rank(method=method)
        
        return {
            'transformed_data': transformed,
            'transform_type': f'Rank Transform ({method})',
            'method': method,
            'metadata': {
                'method': 'rank',
                'parameters': {'method': method}
            }
        }
    
    def zscore_transform(self, data: pd.Series, nan_policy: str = 'omit') -> Dict[str, Any]:
        """
        Apply z-score transformation using scipy.
        
        Args:
            data: Input data series
            nan_policy: How to handle NaN values ('omit', 'raise', 'propagate')
            
        Returns:
            Dictionary containing transformed data and metadata
        """
        transformed_array = stats.zscore(data, nan_policy=nan_policy)
        transformed = pd.Series(transformed_array, index=data.index)
        
        return {
            'transformed_data': transformed,
            'transform_type': 'Z-Score (Scipy)',
            'mean': np.nanmean(data) if nan_policy == 'omit' else np.mean(data),
            'std': np.nanstd(data, ddof=1) if nan_policy == 'omit' else np.std(data, ddof=1),
            'nan_policy': nan_policy,
            'metadata': {
                'method': 'zscore',
                'parameters': {'nan_policy': nan_policy}
            }
        }
    
    def apply_transformation(self, data: pd.Series, transform_type: str, **kwargs) -> Dict[str, Any]:
        """
        Apply specified transformation to data.
        
        Args:
            data: Input data series
            transform_type: Type of transformation to apply
            **kwargs: Additional parameters for specific transformations
            
        Returns:
            Dictionary containing transformation results
        """
        if transform_type not in self.available_transformations:
            raise ValueError(f"Unknown transformation type: {transform_type}")
        
        return self.available_transformations[transform_type](data, **kwargs)
    
    def create_transformation_dataset(self, results: Dict[str, Any], 
                                    original_name: str = 'Original') -> pd.DataFrame:
        """
        Create a new dataset from transformation results.
        
        Args:
            results: Transformation results
            original_name: Name for the original data column
            
        Returns:
            DataFrame containing transformed data
        """
        transform_name = f"{original_name}_{results['metadata']['method']}"
        
        df = pd.DataFrame({
            transform_name: results['transformed_data']
        })
        
        return df
    
    def get_available_transformations(self) -> List[str]:
        """Get list of available transformation types."""
        return list(self.available_transformations.keys())
    
    def generate_transformation_report(self, results: Dict[str, Any]) -> str:
        """Generate a formatted transformation report."""
        report = f"Data Transformation Report\n"
        report += "=" * 30 + "\n\n"
        
        report += f"Transformation Type: {results['transform_type']}\n"
        
        # Add specific information based on transformation type
        metadata = results.get('metadata', {})
        method = metadata.get('method', '')
        params = metadata.get('parameters', {})
        
        if params:
            report += f"Parameters:\n"
            for key, value in params.items():
                if isinstance(value, float):
                    report += f"  {key}: {value:.6f}\n"
                else:
                    report += f"  {key}: {value}\n"
        
        # Add shift information if applicable
        if results.get('shift_applied', False):
            report += f"Data Shift Applied: +{results['shift_value']:.6f}\n"
        
        # Add summary statistics of transformed data
        transformed_data = results['transformed_data']
        report += f"\nTransformed Data Summary:\n"
        report += f"Mean: {transformed_data.mean():.6f}\n"
        report += f"Std: {transformed_data.std():.6f}\n"
        report += f"Min: {transformed_data.min():.6f}\n"
        report += f"Max: {transformed_data.max():.6f}\n"
        
        return report
