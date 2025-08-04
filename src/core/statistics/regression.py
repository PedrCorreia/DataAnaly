"""
Regression Analysis Module

Provides comprehensive regression analysis capabilities.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from scipy import stats
from typing import Dict, Tuple, Optional, List, Any


class RegressionAnalysis:
    """Handles various types of regression analysis."""
    
    def __init__(self):
        self.available_models = {
            'linear': self.linear_regression,
            'polynomial': self.polynomial_regression,
            'ridge': self.ridge_regression,
            'lasso': self.lasso_regression
        }
    
    def linear_regression(self, x: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Perform linear regression analysis.
        
        Args:
            x: Independent variable data
            y: Dependent variable data
            
        Returns:
            Dictionary containing regression results and generated data
        """
        # Reshape if needed
        if x.ndim == 1:
            x = x.reshape(-1, 1)
        
        # Fit model
        model = LinearRegression()
        model.fit(x, y)
        
        # Predictions
        y_pred = model.predict(x)
        
        # Calculate statistics
        r2 = r2_score(y, y_pred)
        mse = mean_squared_error(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        rmse = np.sqrt(mse)
        
        # Residuals
        residuals = y - y_pred
        
        # Generate smooth regression line for plotting
        x_smooth = np.linspace(x.min(), x.max(), 100).reshape(-1, 1)
        y_smooth = model.predict(x_smooth)
        
        # Confidence intervals (simplified)
        n = len(y)
        dof = n - 2  # degrees of freedom
        t_val = stats.t.ppf(0.975, dof)  # 95% confidence
        
        # Standard error of regression
        s_err = np.sqrt(mse)
        
        # Standard error of prediction
        x_mean = np.mean(x)
        se_pred = s_err * np.sqrt(1 + 1/n + (x_smooth.flatten() - x_mean)**2 / np.sum((x.flatten() - x_mean)**2))
        
        # Confidence intervals
        ci_lower = y_smooth.flatten() - t_val * se_pred
        ci_upper = y_smooth.flatten() + t_val * se_pred
        
        return {
            'model_type': 'Linear Regression',
            'slope': float(model.coef_[0]) if len(model.coef_) == 1 else model.coef_.tolist(),
            'intercept': float(model.intercept_),
            'r_squared': float(r2),
            'mse': float(mse),
            'mae': float(mae),
            'rmse': float(rmse),
            'predictions': y_pred,
            'residuals': residuals,
            'x_smooth': x_smooth.flatten(),
            'y_smooth': y_smooth.flatten(),
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'model': model
        }
    
    def polynomial_regression(self, x: np.ndarray, y: np.ndarray, degree: int = 2) -> Dict[str, Any]:
        """
        Perform polynomial regression analysis.
        
        Args:
            x: Independent variable data
            y: Dependent variable data
            degree: Degree of polynomial
            
        Returns:
            Dictionary containing regression results and generated data
        """
        # Reshape if needed
        if x.ndim == 1:
            x = x.reshape(-1, 1)
        
        # Create polynomial features
        poly_features = PolynomialFeatures(degree=degree)
        x_poly = poly_features.fit_transform(x)
        
        # Fit model
        model = LinearRegression()
        model.fit(x_poly, y)
        
        # Predictions
        y_pred = model.predict(x_poly)
        
        # Calculate statistics
        r2 = r2_score(y, y_pred)
        mse = mean_squared_error(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        rmse = np.sqrt(mse)
        
        # Residuals
        residuals = y - y_pred
        
        # Generate smooth curve for plotting
        x_smooth = np.linspace(x.min(), x.max(), 100).reshape(-1, 1)
        x_smooth_poly = poly_features.transform(x_smooth)
        y_smooth = model.predict(x_smooth_poly)
        
        return {
            'model_type': f'Polynomial Regression (degree {degree})',
            'coefficients': model.coef_.tolist(),
            'intercept': float(model.intercept_),
            'degree': degree,
            'r_squared': float(r2),
            'mse': float(mse),
            'mae': float(mae),
            'rmse': float(rmse),
            'predictions': y_pred,
            'residuals': residuals,
            'x_smooth': x_smooth.flatten(),
            'y_smooth': y_smooth.flatten(),
            'model': model,
            'poly_features': poly_features
        }
    
    def ridge_regression(self, x: np.ndarray, y: np.ndarray, alpha: float = 1.0) -> Dict[str, Any]:
        """
        Perform Ridge regression analysis.
        
        Args:
            x: Independent variable data
            y: Dependent variable data
            alpha: Regularization strength
            
        Returns:
            Dictionary containing regression results and generated data
        """
        # Reshape if needed
        if x.ndim == 1:
            x = x.reshape(-1, 1)
        
        # Fit model
        model = Ridge(alpha=alpha)
        model.fit(x, y)
        
        # Predictions
        y_pred = model.predict(x)
        
        # Calculate statistics
        r2 = r2_score(y, y_pred)
        mse = mean_squared_error(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        rmse = np.sqrt(mse)
        
        # Residuals
        residuals = y - y_pred
        
        # Generate smooth regression line for plotting
        x_smooth = np.linspace(x.min(), x.max(), 100).reshape(-1, 1)
        y_smooth = model.predict(x_smooth)
        
        return {
            'model_type': f'Ridge Regression (alpha={alpha})',
            'slope': float(model.coef_[0]) if len(model.coef_) == 1 else model.coef_.tolist(),
            'intercept': float(model.intercept_),
            'alpha': alpha,
            'r_squared': float(r2),
            'mse': float(mse),
            'mae': float(mae),
            'rmse': float(rmse),
            'predictions': y_pred,
            'residuals': residuals,
            'x_smooth': x_smooth.flatten(),
            'y_smooth': y_smooth.flatten(),
            'model': model
        }
    
    def lasso_regression(self, x: np.ndarray, y: np.ndarray, alpha: float = 1.0) -> Dict[str, Any]:
        """
        Perform Lasso regression analysis.
        
        Args:
            x: Independent variable data
            y: Dependent variable data
            alpha: Regularization strength
            
        Returns:
            Dictionary containing regression results and generated data
        """
        # Reshape if needed
        if x.ndim == 1:
            x = x.reshape(-1, 1)
        
        # Fit model
        model = Lasso(alpha=alpha)
        model.fit(x, y)
        
        # Predictions
        y_pred = model.predict(x)
        
        # Calculate statistics
        r2 = r2_score(y, y_pred)
        mse = mean_squared_error(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        rmse = np.sqrt(mse)
        
        # Residuals
        residuals = y - y_pred
        
        # Generate smooth regression line for plotting
        x_smooth = np.linspace(x.min(), x.max(), 100).reshape(-1, 1)
        y_smooth = model.predict(x_smooth)
        
        return {
            'model_type': f'Lasso Regression (alpha={alpha})',
            'slope': float(model.coef_[0]) if len(model.coef_) == 1 else model.coef_.tolist(),
            'intercept': float(model.intercept_),
            'alpha': alpha,
            'r_squared': float(r2),
            'mse': float(mse),
            'mae': float(mae),
            'rmse': float(rmse),
            'predictions': y_pred,
            'residuals': residuals,
            'x_smooth': x_smooth.flatten(),
            'y_smooth': y_smooth.flatten(),
            'model': model
        }
    
    def perform_regression(self, x: np.ndarray, y: np.ndarray, 
                          model_type: str = 'linear', **kwargs) -> Dict[str, Any]:
        """
        Perform regression analysis based on specified model type.
        
        Args:
            x: Independent variable data
            y: Dependent variable data
            model_type: Type of regression model
            **kwargs: Additional parameters for specific models
            
        Returns:
            Dictionary containing regression results and generated data
        """
        if model_type not in self.available_models:
            raise ValueError(f"Unknown model type: {model_type}")
        
        return self.available_models[model_type](x, y, **kwargs)
    
    def create_regression_datasets(self, results: Dict[str, Any], 
                                 original_x_name: str = 'X', 
                                 original_y_name: str = 'Y') -> Dict[str, pd.DataFrame]:
        """
        Create new datasets from regression results that can be saved and plotted.
        
        Args:
            results: Regression analysis results
            original_x_name: Name for original X variable
            original_y_name: Name for original Y variable
            
        Returns:
            Dictionary of DataFrames containing different regression datasets
        """
        datasets = {}
        
        # Regression line dataset
        if 'x_smooth' in results and 'y_smooth' in results:
            regression_df = pd.DataFrame({
                f'{original_x_name}_smooth': results['x_smooth'],
                f'{original_y_name}_regression': results['y_smooth']
            })
            datasets['regression_line'] = regression_df
        
        # Confidence intervals dataset
        if 'ci_lower' in results and 'ci_upper' in results:
            ci_df = pd.DataFrame({
                f'{original_x_name}_smooth': results['x_smooth'],
                f'{original_y_name}_ci_lower': results['ci_lower'],
                f'{original_y_name}_ci_upper': results['ci_upper']
            })
            datasets['confidence_intervals'] = ci_df
        
        # Residuals dataset (if original data is available)
        if 'residuals' in results:
            residuals_df = pd.DataFrame({
                'residuals': results['residuals']
            })
            datasets['residuals'] = residuals_df
        
        # Predictions dataset
        if 'predictions' in results:
            predictions_df = pd.DataFrame({
                f'{original_y_name}_predicted': results['predictions']
            })
            datasets['predictions'] = predictions_df
        
        return datasets
    
    def get_available_models(self) -> List[str]:
        """Get list of available regression model types."""
        return list(self.available_models.keys())
    
    def generate_regression_report(self, results: Dict[str, Any]) -> str:
        """Generate a formatted regression analysis report."""
        report = f"Regression Analysis Report\n"
        report += "=" * 30 + "\n\n"
        
        report += f"Model Type: {results['model_type']}\n"
        
        if 'slope' in results:
            if isinstance(results['slope'], list):
                report += f"Coefficients: {results['slope']}\n"
            else:
                report += f"Slope: {results['slope']:.6f}\n"
        
        if 'intercept' in results:
            report += f"Intercept: {results['intercept']:.6f}\n"
        
        report += f"\nModel Performance:\n"
        report += f"R-squared: {results['r_squared']:.6f}\n"
        report += f"MSE: {results['mse']:.6f}\n"
        report += f"MAE: {results['mae']:.6f}\n"
        report += f"RMSE: {results['rmse']:.6f}\n"
        
        if 'degree' in results:
            report += f"Polynomial Degree: {results['degree']}\n"
        
        if 'alpha' in results:
            report += f"Regularization Alpha: {results['alpha']}\n"
        
        return report
