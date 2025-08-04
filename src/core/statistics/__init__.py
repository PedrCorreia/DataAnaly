"""
Statistics Core Module

This module provides comprehensive statistical analysis capabilities
organized into specialized submodules.
"""

from .descriptive import DescriptiveStatistics
from .regression import RegressionAnalysis
from .transformations import DataTransformations
from .correlation import CorrelationAnalysis
from .hypothesis_testing import HypothesisTests

__all__ = [
    'DescriptiveStatistics',
    'RegressionAnalysis', 
    'DataTransformations',
    'CorrelationAnalysis',
    'HypothesisTests'
]
