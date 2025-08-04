"""
Descriptive Statistics Module

Provides comprehensive descriptive statistical analysis capabilities.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Any, Optional


class DescriptiveStatistics:
    """Handles descriptive statistical calculations."""
    
    def __init__(self):
        self.available_stats = {
            'mean': self.calculate_mean,
            'median': self.calculate_median,
            'mode': self.calculate_mode,
            'std': self.calculate_std,
            'variance': self.calculate_variance,
            'min': self.calculate_min,
            'max': self.calculate_max,
            'range': self.calculate_range,
            'iqr': self.calculate_iqr,
            'q1': self.calculate_q1,
            'q3': self.calculate_q3,
            'skewness': self.calculate_skewness,
            'kurtosis': self.calculate_kurtosis,
            'sem': self.calculate_sem,
            'count': self.calculate_count,
            'sum': self.calculate_sum
        }
    
    def calculate_selected_stats(self, data: pd.Series, selected_stats: List[str]) -> Dict[str, Any]:
        """
        Calculate only the selected descriptive statistics.
        
        Args:
            data: Pandas Series containing the data
            selected_stats: List of statistic names to calculate
            
        Returns:
            Dictionary with statistic names as keys and calculated values
        """
        results = {}
        
        # Only calculate the statistics that are selected
        for stat_name in selected_stats:
            if stat_name in self.available_stats:
                try:
                    results[stat_name] = self.available_stats[stat_name](data)
                except Exception as e:
                    results[stat_name] = f"Error: {str(e)}"
            else:
                results[stat_name] = "Unknown statistic"
        
        return results
    
    def calculate_mean(self, data: pd.Series) -> float:
        """Calculate mean."""
        return float(np.mean(data.dropna()))
    
    def calculate_median(self, data: pd.Series) -> float:
        """Calculate median."""
        return float(np.median(data.dropna()))
    
    def calculate_mode(self, data: pd.Series) -> str:
        """Calculate mode."""
        try:
            mode_result = stats.mode(data.dropna(), keepdims=False)
            if hasattr(mode_result, 'mode'):
                return str(mode_result.mode)
            else:
                return str(mode_result[0])
        except:
            return "No mode"
    
    def calculate_std(self, data: pd.Series) -> float:
        """Calculate standard deviation."""
        return float(np.std(data.dropna(), ddof=1))
    
    def calculate_variance(self, data: pd.Series) -> float:
        """Calculate variance."""
        return float(np.var(data.dropna(), ddof=1))
    
    def calculate_min(self, data: pd.Series) -> float:
        """Calculate minimum."""
        return float(np.min(data.dropna()))
    
    def calculate_max(self, data: pd.Series) -> float:
        """Calculate maximum."""
        return float(np.max(data.dropna()))
    
    def calculate_range(self, data: pd.Series) -> float:
        """Calculate range (max - min)."""
        clean_data = data.dropna()
        return float(np.max(clean_data) - np.min(clean_data))
    
    def calculate_iqr(self, data: pd.Series) -> float:
        """Calculate interquartile range."""
        clean_data = data.dropna()
        q75, q25 = np.percentile(clean_data, [75, 25])
        return float(q75 - q25)
    
    def calculate_q1(self, data: pd.Series) -> float:
        """Calculate first quartile."""
        return float(np.percentile(data.dropna(), 25))
    
    def calculate_q3(self, data: pd.Series) -> float:
        """Calculate third quartile."""
        return float(np.percentile(data.dropna(), 75))
    
    def calculate_skewness(self, data: pd.Series) -> float:
        """Calculate skewness."""
        return float(stats.skew(data.dropna()))
    
    def calculate_kurtosis(self, data: pd.Series) -> float:
        """Calculate kurtosis."""
        return float(stats.kurtosis(data.dropna()))
    
    def calculate_sem(self, data: pd.Series) -> float:
        """Calculate standard error of the mean."""
        return float(stats.sem(data.dropna()))
    
    def calculate_count(self, data: pd.Series) -> int:
        """Calculate count of non-null values."""
        return int(data.count())
    
    def calculate_sum(self, data: pd.Series) -> float:
        """Calculate sum."""
        return float(np.sum(data.dropna()))
    
    def get_available_statistics(self) -> List[str]:
        """Get list of available statistic names."""
        return list(self.available_stats.keys())
    
    def calculate_all_stats(self, data: pd.Series) -> Dict[str, Any]:
        """Calculate all available descriptive statistics."""
        return self.calculate_selected_stats(data, self.get_available_statistics())
    
    def generate_summary_report(self, data: pd.Series, selected_stats: List[str]) -> str:
        """Generate a formatted summary report for selected statistics."""
        results = self.calculate_selected_stats(data, selected_stats)
        
        report = "Descriptive Statistics Summary\n"
        report += "=" * 30 + "\n\n"
        
        for stat_name, value in results.items():
            if isinstance(value, float):
                report += f"{stat_name.capitalize()}: {value:.4f}\n"
            else:
                report += f"{stat_name.capitalize()}: {value}\n"
        
        return report
