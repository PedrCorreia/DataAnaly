"""
Hypothesis Testing Module

Provides statistical hypothesis testing capabilities.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Any, Optional, Tuple


class HypothesisTests:
    """Handles various statistical hypothesis tests."""
    
    def __init__(self):
        self.available_tests = {
            't_test_one_sample': self.one_sample_t_test,
            't_test_two_sample': self.two_sample_t_test,
            't_test_paired': self.paired_t_test,
            'z_test_one_sample': self.one_sample_z_test,
            'chi_square_goodness': self.chi_square_goodness_of_fit,
            'chi_square_independence': self.chi_square_independence,
            'anova_one_way': self.one_way_anova,
            'shapiro_wilk': self.shapiro_wilk_test,
            'kolmogorov_smirnov': self.kolmogorov_smirnov_test,
            'mann_whitney': self.mann_whitney_test,
            'wilcoxon': self.wilcoxon_test,
            'kruskal_wallis': self.kruskal_wallis_test
        }
    
    def one_sample_t_test(self, data: pd.Series, mu0: float = 0, 
                         alternative: str = 'two-sided') -> Dict[str, Any]:
        """
        Perform one-sample t-test.
        
        Args:
            data: Sample data
            mu0: Hypothesized population mean
            alternative: Type of test ('two-sided', 'less', 'greater')
            
        Returns:
            Dictionary containing test results
        """
        clean_data = data.dropna()
        
        if len(clean_data) < 2:
            return {
                'test_type': 'One-Sample t-test',
                'error': 'Insufficient data points',
                'n_samples': len(clean_data)
            }
        
        t_stat, p_value = stats.ttest_1samp(clean_data, mu0, alternative=alternative)
        
        # Calculate confidence interval
        n = len(clean_data)
        df = n - 1
        se = stats.sem(clean_data)
        t_crit = stats.t.ppf(0.975, df)  # 95% CI
        mean_val = np.mean(clean_data)
        ci_lower = mean_val - t_crit * se
        ci_upper = mean_val + t_crit * se
        
        return {
            'test_type': 'One-Sample t-test',
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'degrees_of_freedom': int(df),
            'sample_mean': float(mean_val),
            'hypothesized_mean': float(mu0),
            'sample_size': int(n),
            'alternative': alternative,
            'ci_lower': float(ci_lower),
            'ci_upper': float(ci_upper),
            'significant': p_value < 0.05,
            'conclusion': 'Reject H0' if p_value < 0.05 else 'Fail to reject H0'
        }
    
    def two_sample_t_test(self, group1: pd.Series, group2: pd.Series,
                         equal_var: bool = True, alternative: str = 'two-sided') -> Dict[str, Any]:
        """
        Perform two-sample t-test.
        
        Args:
            group1: First group data
            group2: Second group data
            equal_var: Assume equal variances
            alternative: Type of test ('two-sided', 'less', 'greater')
            
        Returns:
            Dictionary containing test results
        """
        clean_group1 = group1.dropna()
        clean_group2 = group2.dropna()
        
        if len(clean_group1) < 2 or len(clean_group2) < 2:
            return {
                'test_type': 'Two-Sample t-test',
                'error': 'Insufficient data points in one or both groups',
                'n_group1': len(clean_group1),
                'n_group2': len(clean_group2)
            }
        
        t_stat, p_value = stats.ttest_ind(clean_group1, clean_group2, 
                                         equal_var=equal_var, alternative=alternative)
        
        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt(((len(clean_group1) - 1) * np.var(clean_group1, ddof=1) + 
                             (len(clean_group2) - 1) * np.var(clean_group2, ddof=1)) / 
                            (len(clean_group1) + len(clean_group2) - 2))
        cohens_d = (np.mean(clean_group1) - np.mean(clean_group2)) / pooled_std
        
        return {
            'test_type': 'Two-Sample t-test (Independent)',
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'group1_mean': float(np.mean(clean_group1)),
            'group2_mean': float(np.mean(clean_group2)),
            'group1_size': int(len(clean_group1)),
            'group2_size': int(len(clean_group2)),
            'equal_variances': equal_var,
            'alternative': alternative,
            'cohens_d': float(cohens_d),
            'significant': p_value < 0.05,
            'conclusion': 'Reject H0' if p_value < 0.05 else 'Fail to reject H0'
        }
    
    def paired_t_test(self, before: pd.Series, after: pd.Series,
                     alternative: str = 'two-sided') -> Dict[str, Any]:
        """
        Perform paired t-test.
        
        Args:
            before: Before measurements
            after: After measurements
            alternative: Type of test ('two-sided', 'less', 'greater')
            
        Returns:
            Dictionary containing test results
        """
        # Align the series and remove NaN pairs
        paired_data = pd.DataFrame({'before': before, 'after': after}).dropna()
        
        if len(paired_data) < 2:
            return {
                'test_type': 'Paired t-test',
                'error': 'Insufficient paired data points',
                'n_pairs': len(paired_data)
            }
        
        t_stat, p_value = stats.ttest_rel(paired_data['before'], paired_data['after'],
                                         alternative=alternative)
        
        # Calculate difference statistics
        differences = paired_data['after'] - paired_data['before']
        mean_diff = np.mean(differences)
        
        # Effect size for paired t-test
        cohens_d = mean_diff / np.std(differences, ddof=1)
        
        return {
            'test_type': 'Paired t-test',
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'mean_difference': float(mean_diff),
            'before_mean': float(np.mean(paired_data['before'])),
            'after_mean': float(np.mean(paired_data['after'])),
            'n_pairs': int(len(paired_data)),
            'alternative': alternative,
            'cohens_d': float(cohens_d),
            'significant': p_value < 0.05,
            'conclusion': 'Reject H0' if p_value < 0.05 else 'Fail to reject H0'
        }
    
    def one_sample_z_test(self, data: pd.Series, mu0: float = 0, sigma: float = 1,
                         alternative: str = 'two-sided') -> Dict[str, Any]:
        """
        Perform one-sample z-test.
        
        Args:
            data: Sample data
            mu0: Hypothesized population mean
            sigma: Known population standard deviation
            alternative: Type of test ('two-sided', 'less', 'greater')
            
        Returns:
            Dictionary containing test results
        """
        clean_data = data.dropna()
        
        if len(clean_data) < 1:
            return {
                'test_type': 'One-Sample z-test',
                'error': 'No valid data points',
                'n_samples': len(clean_data)
            }
        
        n = len(clean_data)
        sample_mean = np.mean(clean_data)
        se = sigma / np.sqrt(n)
        z_stat = (sample_mean - mu0) / se
        
        # Calculate p-value based on alternative hypothesis
        if alternative == 'two-sided':
            p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
        elif alternative == 'less':
            p_value = stats.norm.cdf(z_stat)
        elif alternative == 'greater':
            p_value = 1 - stats.norm.cdf(z_stat)
        else:
            raise ValueError("Alternative must be 'two-sided', 'less', or 'greater'")
        
        # Confidence interval
        z_crit = stats.norm.ppf(0.975)  # 95% CI
        ci_lower = sample_mean - z_crit * se
        ci_upper = sample_mean + z_crit * se
        
        return {
            'test_type': 'One-Sample z-test',
            'z_statistic': float(z_stat),
            'p_value': float(p_value),
            'sample_mean': float(sample_mean),
            'hypothesized_mean': float(mu0),
            'population_std': float(sigma),
            'sample_size': int(n),
            'alternative': alternative,
            'ci_lower': float(ci_lower),
            'ci_upper': float(ci_upper),
            'significant': p_value < 0.05,
            'conclusion': 'Reject H0' if p_value < 0.05 else 'Fail to reject H0'
        }
    
    def shapiro_wilk_test(self, data: pd.Series) -> Dict[str, Any]:
        """
        Perform Shapiro-Wilk test for normality.
        
        Args:
            data: Sample data
            
        Returns:
            Dictionary containing test results
        """
        clean_data = data.dropna()
        
        if len(clean_data) < 3:
            return {
                'test_type': 'Shapiro-Wilk Test',
                'error': 'Insufficient data points (minimum 3 required)',
                'n_samples': len(clean_data)
            }
        
        if len(clean_data) > 5000:
            return {
                'test_type': 'Shapiro-Wilk Test',
                'error': 'Too many data points (maximum 5000)',
                'n_samples': len(clean_data)
            }
        
        stat, p_value = stats.shapiro(clean_data)
        
        return {
            'test_type': 'Shapiro-Wilk Test for Normality',
            'w_statistic': float(stat),
            'p_value': float(p_value),
            'sample_size': int(len(clean_data)),
            'significant': p_value < 0.05,
            'conclusion': 'Data is not normally distributed' if p_value < 0.05 else 'Data appears normally distributed',
            'interpretation': 'Reject normality assumption' if p_value < 0.05 else 'Fail to reject normality assumption'
        }
    
    def chi_square_goodness_of_fit(self, observed: np.ndarray, expected: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Perform Chi-square goodness of fit test.
        
        Args:
            observed: Observed frequencies
            expected: Expected frequencies (if None, assumes uniform distribution)
            
        Returns:
            Dictionary containing test results
        """
        observed = np.array(observed)
        
        if expected is None:
            # Uniform distribution
            expected = np.full_like(observed, np.mean(observed), dtype=float)
        else:
            expected = np.array(expected)
        
        if len(observed) != len(expected):
            return {
                'test_type': 'Chi-square Goodness of Fit',
                'error': 'Observed and expected arrays must have same length'
            }
        
        chi2_stat, p_value = stats.chisquare(observed, expected)
        dof = len(observed) - 1
        
        return {
            'test_type': 'Chi-square Goodness of Fit',
            'chi2_statistic': float(chi2_stat),
            'p_value': float(p_value),
            'degrees_of_freedom': int(dof),
            'observed': observed.tolist(),
            'expected': expected.tolist(),
            'significant': p_value < 0.05,
            'conclusion': 'Reject H0 (distributions differ)' if p_value < 0.05 else 'Fail to reject H0 (good fit)'
        }
    
    def chi_square_independence(self, contingency_table: np.ndarray) -> Dict[str, Any]:
        """
        Perform Chi-square test of independence.
        
        Args:
            contingency_table: 2D contingency table
            
        Returns:
            Dictionary containing test results
        """
        contingency_table = np.array(contingency_table)
        
        if contingency_table.ndim != 2:
            return {
                'test_type': 'Chi-square Test of Independence',
                'error': 'Contingency table must be 2-dimensional'
            }
        
        chi2_stat, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        return {
            'test_type': 'Chi-square Test of Independence',
            'chi2_statistic': float(chi2_stat),
            'p_value': float(p_value),
            'degrees_of_freedom': int(dof),
            'observed': contingency_table.tolist(),
            'expected': expected.tolist(),
            'significant': p_value < 0.05,
            'conclusion': 'Reject H0 (variables are dependent)' if p_value < 0.05 else 'Fail to reject H0 (variables are independent)'
        }
    
    def one_way_anova(self, *groups: pd.Series) -> Dict[str, Any]:
        """
        Perform one-way ANOVA.
        
        Args:
            *groups: Variable number of group data series
            
        Returns:
            Dictionary containing test results
        """
        if len(groups) < 2:
            return {
                'test_type': 'One-way ANOVA',
                'error': 'At least 2 groups required for ANOVA'
            }
        
        # Clean data for each group
        clean_groups = []
        group_sizes = []
        group_means = []
        
        for i, group in enumerate(groups):
            clean_group = group.dropna()
            if len(clean_group) < 2:
                return {
                    'test_type': 'One-way ANOVA',
                    'error': f'Group {i+1} has insufficient data points (minimum 2 required)',
                    'group_sizes': [len(g.dropna()) for g in groups]
                }
            clean_groups.append(clean_group)
            group_sizes.append(len(clean_group))
            group_means.append(float(np.mean(clean_group)))
        
        # Perform ANOVA
        f_stat, p_value = stats.f_oneway(*clean_groups)
        
        # Calculate effect size (eta-squared)
        total_mean = np.mean(np.concatenate(clean_groups))
        ss_between = sum(len(group) * (np.mean(group) - total_mean)**2 for group in clean_groups)
        ss_total = sum(sum((x - total_mean)**2 for x in group) for group in clean_groups)
        eta_squared = ss_between / ss_total if ss_total > 0 else 0
        
        return {
            'test_type': 'One-way ANOVA',
            'f_statistic': float(f_stat),
            'p_value': float(p_value),
            'num_groups': len(groups),
            'group_sizes': group_sizes,
            'group_means': group_means,
            'eta_squared': float(eta_squared),
            'significant': p_value < 0.05,
            'conclusion': 'Reject H0 (group means differ)' if p_value < 0.05 else 'Fail to reject H0 (no significant difference)'
        }
    
    def kolmogorov_smirnov_test(self, data: pd.Series, distribution: str = 'norm') -> Dict[str, Any]:
        """
        Perform Kolmogorov-Smirnov test for goodness of fit.
        
        Args:
            data: Sample data
            distribution: Distribution to test against ('norm', 'uniform', 'expon')
            
        Returns:
            Dictionary containing test results
        """
        clean_data = data.dropna()
        
        if len(clean_data) < 3:
            return {
                'test_type': 'Kolmogorov-Smirnov Test',
                'error': 'Insufficient data points (minimum 3 required)',
                'n_samples': len(clean_data)
            }
        
        if distribution == 'norm':
            # Test against normal distribution
            stat, p_value = stats.kstest(clean_data, 'norm', 
                                       args=(np.mean(clean_data), np.std(clean_data, ddof=1)))
            dist_name = 'Normal'
        elif distribution == 'uniform':
            # Test against uniform distribution
            stat, p_value = stats.kstest(clean_data, 'uniform', 
                                       args=(np.min(clean_data), np.max(clean_data) - np.min(clean_data)))
            dist_name = 'Uniform'
        elif distribution == 'expon':
            # Test against exponential distribution
            stat, p_value = stats.kstest(clean_data, 'expon', 
                                       args=(np.min(clean_data), np.mean(clean_data) - np.min(clean_data)))
            dist_name = 'Exponential'
        else:
            return {
                'test_type': 'Kolmogorov-Smirnov Test',
                'error': f'Unknown distribution: {distribution}'
            }
        
        return {
            'test_type': f'Kolmogorov-Smirnov Test ({dist_name})',
            'ks_statistic': float(stat),
            'p_value': float(p_value),
            'sample_size': int(len(clean_data)),
            'distribution': dist_name,
            'significant': p_value < 0.05,
            'conclusion': f'Reject H0 (data does not follow {dist_name} distribution)' if p_value < 0.05 else f'Fail to reject H0 (data follows {dist_name} distribution)',
            'interpretation': f'Data does not fit {dist_name} distribution' if p_value < 0.05 else f'Data appears to fit {dist_name} distribution'
        }
    
    def wilcoxon_test(self, before: pd.Series, after: pd.Series, alternative: str = 'two-sided') -> Dict[str, Any]:
        """
        Perform Wilcoxon signed-rank test (non-parametric alternative to paired t-test).
        
        Args:
            before: Before measurements
            after: After measurements
            alternative: Type of test ('two-sided', 'less', 'greater')
            
        Returns:
            Dictionary containing test results
        """
        # Align the series and remove NaN pairs
        paired_data = pd.DataFrame({'before': before, 'after': after}).dropna()
        
        if len(paired_data) < 3:
            return {
                'test_type': 'Wilcoxon Signed-Rank Test',
                'error': 'Insufficient paired data points (minimum 3 required)',
                'n_pairs': len(paired_data)
            }
        
        # Calculate differences
        differences = paired_data['after'] - paired_data['before']
        
        # Remove zero differences
        differences = differences[differences != 0]
        
        if len(differences) < 3:
            return {
                'test_type': 'Wilcoxon Signed-Rank Test',
                'error': 'Insufficient non-zero differences',
                'n_nonzero_diff': len(differences)
            }
        
        stat, p_value = stats.wilcoxon(differences, alternative=alternative)
        
        return {
            'test_type': 'Wilcoxon Signed-Rank Test',
            'w_statistic': float(stat),
            'p_value': float(p_value),
            'n_pairs': int(len(paired_data)),
            'n_nonzero_diff': int(len(differences)),
            'median_difference': float(np.median(differences)),
            'alternative': alternative,
            'significant': p_value < 0.05,
            'conclusion': 'Reject H0 (significant difference)' if p_value < 0.05 else 'Fail to reject H0 (no significant difference)'
        }
    
    def kruskal_wallis_test(self, *groups: pd.Series) -> Dict[str, Any]:
        """
        Perform Kruskal-Wallis test (non-parametric alternative to one-way ANOVA).
        
        Args:
            *groups: Variable number of group data series
            
        Returns:
            Dictionary containing test results
        """
        if len(groups) < 2:
            return {
                'test_type': 'Kruskal-Wallis Test',
                'error': 'At least 2 groups required'
            }
        
        # Clean data for each group
        clean_groups = []
        group_sizes = []
        group_medians = []
        
        for i, group in enumerate(groups):
            clean_group = group.dropna()
            if len(clean_group) < 1:
                return {
                    'test_type': 'Kruskal-Wallis Test',
                    'error': f'Group {i+1} has no valid data points',
                    'group_sizes': [len(g.dropna()) for g in groups]
                }
            clean_groups.append(clean_group)
            group_sizes.append(len(clean_group))
            group_medians.append(float(np.median(clean_group)))
        
        # Perform Kruskal-Wallis test
        h_stat, p_value = stats.kruskal(*clean_groups)
        
        return {
            'test_type': 'Kruskal-Wallis Test',
            'h_statistic': float(h_stat),
            'p_value': float(p_value),
            'num_groups': len(groups),
            'group_sizes': group_sizes,
            'group_medians': group_medians,
            'significant': p_value < 0.05,
            'conclusion': 'Reject H0 (group distributions differ)' if p_value < 0.05 else 'Fail to reject H0 (no significant difference)'
        }
    
    def mann_whitney_test(self, group1: pd.Series, group2: pd.Series,
                         alternative: str = 'two-sided') -> Dict[str, Any]:
        """
        Perform Mann-Whitney U test (non-parametric alternative to two-sample t-test).
        
        Args:
            group1: First group data
            group2: Second group data
            alternative: Type of test ('two-sided', 'less', 'greater')
            
        Returns:
            Dictionary containing test results
        """
        clean_group1 = group1.dropna()
        clean_group2 = group2.dropna()
        
        if len(clean_group1) < 1 or len(clean_group2) < 1:
            return {
                'test_type': 'Mann-Whitney U Test',
                'error': 'Insufficient data points in one or both groups',
                'n_group1': len(clean_group1),
                'n_group2': len(clean_group2)
            }
        
        stat, p_value = stats.mannwhitneyu(clean_group1, clean_group2, 
                                          alternative=alternative)
        
        return {
            'test_type': 'Mann-Whitney U Test',
            'u_statistic': float(stat),
            'p_value': float(p_value),
            'group1_median': float(np.median(clean_group1)),
            'group2_median': float(np.median(clean_group2)),
            'group1_size': int(len(clean_group1)),
            'group2_size': int(len(clean_group2)),
            'alternative': alternative,
            'significant': p_value < 0.05,
            'conclusion': 'Reject H0 (groups differ)' if p_value < 0.05 else 'Fail to reject H0 (no difference)'
        }
    
    def perform_test(self, test_type: str, **kwargs) -> Dict[str, Any]:
        """
        Perform specified hypothesis test.
        
        Args:
            test_type: Type of test to perform
            **kwargs: Test-specific parameters
            
        Returns:
            Dictionary containing test results
        """
        if test_type not in self.available_tests:
            raise ValueError(f"Unknown test type: {test_type}")
        
        return self.available_tests[test_type](**kwargs)
    
    def get_available_tests(self) -> List[str]:
        """Get list of available hypothesis tests."""
        return list(self.available_tests.keys())
    
    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """Generate a formatted hypothesis test report."""
        report = f"Hypothesis Test Report\n"
        report += "=" * 30 + "\n\n"
        
        report += f"Test Type: {results['test_type']}\n"
        
        if 'error' in results:
            report += f"Error: {results['error']}\n"
            return report
        
        # Add test-specific statistics
        if 't_statistic' in results:
            report += f"t-statistic: {results['t_statistic']:.6f}\n"
        if 'z_statistic' in results:
            report += f"z-statistic: {results['z_statistic']:.6f}\n"
        if 'u_statistic' in results:
            report += f"U-statistic: {results['u_statistic']:.6f}\n"
        if 'w_statistic' in results:
            report += f"W-statistic: {results['w_statistic']:.6f}\n"
        
        report += f"p-value: {results['p_value']:.6f}\n"
        
        # Add sample information
        if 'sample_size' in results:
            report += f"Sample Size: {results['sample_size']}\n"
        if 'n_pairs' in results:
            report += f"Number of Pairs: {results['n_pairs']}\n"
        if 'group1_size' in results and 'group2_size' in results:
            report += f"Group 1 Size: {results['group1_size']}\n"
            report += f"Group 2 Size: {results['group2_size']}\n"
        
        # Add means/medians
        if 'sample_mean' in results:
            report += f"Sample Mean: {results['sample_mean']:.6f}\n"
        if 'group1_mean' in results:
            report += f"Group 1 Mean: {results['group1_mean']:.6f}\n"
            report += f"Group 2 Mean: {results['group2_mean']:.6f}\n"
        if 'group1_median' in results:
            report += f"Group 1 Median: {results['group1_median']:.6f}\n"
            report += f"Group 2 Median: {results['group2_median']:.6f}\n"
        
        # Add confidence intervals
        if 'ci_lower' in results and 'ci_upper' in results:
            report += f"95% CI: [{results['ci_lower']:.6f}, {results['ci_upper']:.6f}]\n"
        
        # Add effect size
        if 'cohens_d' in results:
            report += f"Cohen's d: {results['cohens_d']:.6f}\n"
        
        # Add conclusion
        report += f"\nSignificant (α = 0.05): {results['significant']}\n"
        report += f"Conclusion: {results['conclusion']}\n"
        
        if 'interpretation' in results:
            report += f"Interpretation: {results['interpretation']}\n"
        
        return report
