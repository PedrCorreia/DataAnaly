"""
Correlation Analysis Module

Provides correlation analysis capabilities.
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import spearmanr, kendalltau
from typing import Dict, List, Any, Optional, Tuple


class CorrelationAnalysis:
    """Handles correlation analysis between variables."""
    
    def __init__(self):
        self.available_methods = {
            'pearson': self.pearson_correlation,
            'spearman': self.spearman_correlation,
            'kendall': self.kendall_correlation
        }
    
    def pearson_correlation(self, x: pd.Series, y: pd.Series) -> Dict[str, Any]:
        """
        Calculate Pearson correlation coefficient.
        
        Args:
            x: First variable
            y: Second variable
            
        Returns:
            Dictionary containing correlation results
        """
        # Remove NaN values
        valid_data = pd.DataFrame({'x': x, 'y': y}).dropna()
        
        if len(valid_data) < 2:
            return {
                'correlation': np.nan,
                'p_value': np.nan,
                'n_samples': len(valid_data),
                'method': 'Pearson',
                'error': 'Insufficient valid data points'
            }
        
        corr, p_value = stats.pearsonr(valid_data['x'], valid_data['y'])
        
        # Calculate confidence interval
        n = len(valid_data)
        if n > 3:
            # Fisher's z-transformation for confidence interval
            z = np.arctanh(corr)
            se = 1 / np.sqrt(n - 3)
            z_crit = stats.norm.ppf(0.975)  # 95% confidence
            z_lower = z - z_crit * se
            z_upper = z + z_crit * se
            ci_lower = np.tanh(z_lower)
            ci_upper = np.tanh(z_upper)
        else:
            ci_lower = np.nan
            ci_upper = np.nan
        
        return {
            'correlation': float(corr),
            'p_value': float(p_value),
            'n_samples': int(n),
            'method': 'Pearson',
            'ci_lower': float(ci_lower) if not np.isnan(ci_lower) else None,
            'ci_upper': float(ci_upper) if not np.isnan(ci_upper) else None,
            'significance': 'Significant' if p_value < 0.05 else 'Not Significant'
        }
    
    def spearman_correlation(self, x: pd.Series, y: pd.Series) -> Dict[str, Any]:
        """
        Calculate Spearman rank correlation coefficient.
        
        Args:
            x: First variable
            y: Second variable
            
        Returns:
            Dictionary containing correlation results
        """
        # Remove NaN values
        valid_data = pd.DataFrame({'x': x, 'y': y}).dropna()
        
        if len(valid_data) < 2:
            return {
                'correlation': np.nan,
                'p_value': np.nan,
                'n_samples': len(valid_data),
                'method': 'Spearman',
                'error': 'Insufficient valid data points'
            }
        
        corr, p_value = spearmanr(valid_data['x'], valid_data['y'])
        
        return {
            'correlation': float(corr),
            'p_value': float(p_value),
            'n_samples': int(len(valid_data)),
            'method': 'Spearman',
            'significance': 'Significant' if p_value < 0.05 else 'Not Significant'
        }
    
    def kendall_correlation(self, x: pd.Series, y: pd.Series) -> Dict[str, Any]:
        """
        Calculate Kendall's tau correlation coefficient.
        
        Args:
            x: First variable
            y: Second variable
            
        Returns:
            Dictionary containing correlation results
        """
        # Remove NaN values
        valid_data = pd.DataFrame({'x': x, 'y': y}).dropna()
        
        if len(valid_data) < 2:
            return {
                'correlation': np.nan,
                'p_value': np.nan,
                'n_samples': len(valid_data),
                'method': 'Kendall',
                'error': 'Insufficient valid data points'
            }
        
        corr, p_value = kendalltau(valid_data['x'], valid_data['y'])
        
        return {
            'correlation': float(corr),
            'p_value': float(p_value),
            'n_samples': int(len(valid_data)),
            'method': 'Kendall',
            'significance': 'Significant' if p_value < 0.05 else 'Not Significant'
        }
    
    def correlation_matrix(self, data: pd.DataFrame, method: str = 'pearson') -> Dict[str, Any]:
        """
        Calculate correlation matrix for multiple variables.
        
        Args:
            data: DataFrame with multiple variables
            method: Correlation method ('pearson', 'spearman', 'kendall')
            
        Returns:
            Dictionary containing correlation matrix and p-values
        """
        if method == 'pearson':
            corr_matrix = data.corr(method='pearson')
            
            # Calculate p-values for each pair
            n_vars = len(data.columns)
            p_values = np.zeros((n_vars, n_vars))
            
            for i in range(n_vars):
                for j in range(n_vars):
                    if i != j:
                        valid_data = data.iloc[:, [i, j]].dropna()
                        if len(valid_data) > 2:
                            _, p_val = stats.pearsonr(valid_data.iloc[:, 0], valid_data.iloc[:, 1])
                            p_values[i, j] = p_val
                        else:
                            p_values[i, j] = np.nan
                    else:
                        p_values[i, j] = 0.0  # Diagonal elements
            
            p_matrix = pd.DataFrame(p_values, index=data.columns, columns=data.columns)
            
        elif method == 'spearman':
            corr_matrix = data.corr(method='spearman')
            
            # Calculate p-values for Spearman
            n_vars = len(data.columns)
            p_values = np.zeros((n_vars, n_vars))
            
            for i in range(n_vars):
                for j in range(n_vars):
                    if i != j:
                        valid_data = data.iloc[:, [i, j]].dropna()
                        if len(valid_data) > 2:
                            _, p_val = spearmanr(valid_data.iloc[:, 0], valid_data.iloc[:, 1])
                            p_values[i, j] = p_val
                        else:
                            p_values[i, j] = np.nan
                    else:
                        p_values[i, j] = 0.0
            
            p_matrix = pd.DataFrame(p_values, index=data.columns, columns=data.columns)
            
        elif method == 'kendall':
            corr_matrix = data.corr(method='kendall')
            
            # Calculate p-values for Kendall
            n_vars = len(data.columns)
            p_values = np.zeros((n_vars, n_vars))
            
            for i in range(n_vars):
                for j in range(n_vars):
                    if i != j:
                        valid_data = data.iloc[:, [i, j]].dropna()
                        if len(valid_data) > 2:
                            _, p_val = kendalltau(valid_data.iloc[:, 0], valid_data.iloc[:, 1])
                            p_values[i, j] = p_val
                        else:
                            p_values[i, j] = np.nan
                    else:
                        p_values[i, j] = 0.0
            
            p_matrix = pd.DataFrame(p_values, index=data.columns, columns=data.columns)
            
        else:
            raise ValueError("Method must be 'pearson', 'spearman', or 'kendall'")
        
        return {
            'correlation_matrix': corr_matrix,
            'p_value_matrix': p_matrix,
            'method': method.title(),
            'n_variables': len(data.columns),
            'variable_names': list(data.columns)
        }
    
    def partial_correlation(self, x: pd.Series, y: pd.Series, control: pd.Series) -> Dict[str, Any]:
        """
        Calculate partial correlation between x and y, controlling for control variable.
        
        Args:
            x: First variable
            y: Second variable
            control: Control variable
            
        Returns:
            Dictionary containing partial correlation results
        """
        # Remove NaN values
        valid_data = pd.DataFrame({'x': x, 'y': y, 'control': control}).dropna()
        
        if len(valid_data) < 4:
            return {
                'partial_correlation': np.nan,
                'n_samples': len(valid_data),
                'error': 'Insufficient valid data points'
            }
        
        # Calculate correlations
        r_xy = stats.pearsonr(valid_data['x'], valid_data['y'])[0]
        r_xz = stats.pearsonr(valid_data['x'], valid_data['control'])[0]
        r_yz = stats.pearsonr(valid_data['y'], valid_data['control'])[0]
        
        # Calculate partial correlation
        numerator = r_xy - r_xz * r_yz
        denominator = np.sqrt((1 - r_xz**2) * (1 - r_yz**2))
        
        if denominator == 0:
            partial_corr = np.nan
        else:
            partial_corr = numerator / denominator
        
        # Calculate degrees of freedom and t-statistic for p-value
        n = len(valid_data)
        df = n - 3
        
        if not np.isnan(partial_corr) and df > 0:
            t_stat = partial_corr * np.sqrt(df / (1 - partial_corr**2))
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df))
        else:
            p_value = np.nan
        
        return {
            'partial_correlation': float(partial_corr) if not np.isnan(partial_corr) else None,
            'p_value': float(p_value) if not np.isnan(p_value) else None,
            'n_samples': int(n),
            'degrees_of_freedom': int(df) if df > 0 else None,
            'r_xy': float(r_xy),
            'r_xz': float(r_xz),
            'r_yz': float(r_yz),
            'significance': 'Significant' if not np.isnan(p_value) and p_value < 0.05 else 'Not Significant'
        }
    
    def calculate_correlation(self, x: pd.Series, y: pd.Series, 
                            method: str = 'pearson') -> Dict[str, Any]:
        """
        Calculate correlation between two variables using specified method.
        
        Args:
            x: First variable
            y: Second variable
            method: Correlation method ('pearson', 'spearman', 'kendall')
            
        Returns:
            Dictionary containing correlation results
        """
        if method not in self.available_methods:
            raise ValueError(f"Unknown correlation method: {method}")
        
        return self.available_methods[method](x, y)
    
    def get_available_methods(self) -> List[str]:
        """Get list of available correlation methods."""
        return list(self.available_methods.keys())
    
    def generate_correlation_report(self, results: Dict[str, Any]) -> str:
        """Generate a formatted correlation analysis report."""
        if 'correlation_matrix' in results:
            # Matrix report
            report = f"Correlation Matrix Report ({results['method']})\n"
            report += "=" * 40 + "\n\n"
            
            report += f"Number of variables: {results['n_variables']}\n"
            report += f"Variables: {', '.join(results['variable_names'])}\n\n"
            
            report += "Correlation Matrix:\n"
            report += str(results['correlation_matrix'].round(4)) + "\n\n"
            
            report += "P-value Matrix:\n"
            report += str(results['p_value_matrix'].round(4)) + "\n"
            
        else:
            # Single correlation report
            report = f"Correlation Analysis Report\n"
            report += "=" * 30 + "\n\n"
            
            report += f"Method: {results['method']}\n"
            report += f"Sample Size: {results['n_samples']}\n"
            
            if 'error' in results:
                report += f"Error: {results['error']}\n"
            else:
                report += f"Correlation: {results['correlation']:.6f}\n"
                report += f"P-value: {results['p_value']:.6f}\n"
                report += f"Significance: {results['significance']}\n"
                
                if 'ci_lower' in results and results['ci_lower'] is not None:
                    report += f"95% CI: [{results['ci_lower']:.6f}, {results['ci_upper']:.6f}]\n"
                
                # Interpret correlation strength
                abs_corr = abs(results['correlation'])
                if abs_corr < 0.1:
                    strength = "Negligible"
                elif abs_corr < 0.3:
                    strength = "Weak"
                elif abs_corr < 0.5:
                    strength = "Moderate"
                elif abs_corr < 0.7:
                    strength = "Strong"
                else:
                    strength = "Very Strong"
                
                direction = "Positive" if results['correlation'] > 0 else "Negative"
                report += f"Interpretation: {strength} {direction} correlation\n"
        
        return report
