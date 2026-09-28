"""
Week 3 Task: Statistical Analysis and Hypothesis Testing in Python
Candidate: ksangam990
Domain: Gemological Valuation & Luxury Commodity Econometrics
Topic: Empirical Validation of Valuation Premia: One-Way ANOVA, Welch's t-Test, and Chi-Square Tests on Diamond Pricing
"""

import os
import urllib.request
import pandas as pd
import numpy as np
import scipy.stats as stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import matplotlib.pyplot as plt
import seaborn as sns
import json

# Visual configuration
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.sans-serif': 'Arial',
    'font.family': 'sans-serif',
    'figure.titlesize': 13,
    'axes.titlesize': 11,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'figure.autolayout': True
})

DATA_RAW_URL = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/diamonds.csv"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "diamonds_raw.csv")
CLEANED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "diamonds_cleaned.csv")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
METRICS_PATH = os.path.join(BASE_DIR, "data", "processed", "hypothesis_testing_metrics.json")


def acquire_data():
    """Acquires raw diamonds dataset from public repository."""
    print("=" * 60)
    print("STEP 1: DATA ACQUISITION")
    print("=" * 60)
    os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
    if not os.path.exists(RAW_DATA_PATH):
        print(f"Downloading dataset from: {DATA_RAW_URL}...")
        urllib.request.urlretrieve(DATA_RAW_URL, RAW_DATA_PATH)
        print(f"Raw data saved: {RAW_DATA_PATH}")
    else:
        print(f"Raw data exists: {RAW_DATA_PATH}")

    df_raw = pd.read_csv(RAW_DATA_PATH)
    print(f"Acquired dataset shape: {df_raw.shape[0]} diamonds, {df_raw.shape[1]} columns")
    return df_raw


def clean_and_prepare(df_raw):
    """Cleans data and engineers price-per-carat and color tiers."""
    print("\n" + "=" * 60)
    print("STEP 2: DATA CLEANING & METRIC PREPARATION")
    print("=" * 60)

    df = df_raw.copy()

    # 1. Deduplication
    dup_count = int(df.duplicated().sum())
    print(f"Duplicate rows detected: {dup_count}")
    if dup_count > 0:
        df = df.drop_duplicates().reset_index(drop=True)

    # 2. Filter unphysical dimensional outliers (diamonds with x, y, or z <= 0)
    invalid_dim = ((df['x'] <= 0) | (df['y'] <= 0) | (df['z'] <= 0)).sum()
    print(f"Unphysical zero-dimension records removed: {invalid_dim}")
    df = df[(df['x'] > 0) & (df['y'] > 0) & (df['z'] > 0)].copy()

    # 3. Feature Engineering: Price-per-Carat
    df['price_per_carat'] = df['price'] / df['carat']

    # 4. Color Classification
    df['color_tier'] = df['color'].apply(lambda c: 'Colorless (D-F)' if c in ['D', 'E', 'F'] else 'Near-Colorless (G-J)')

    # Order cuts and clarities categorically
    cut_order = ['Fair', 'Good', 'Very Good', 'Premium', 'Ideal']
    df['cut'] = pd.Categorical(df['cut'], categories=cut_order, ordered=True)

    clarity_order = ['I1', 'SI2', 'SI1', 'VS2', 'VS1', 'VVS2', 'VVS1', 'IF']
    df['clarity'] = pd.Categorical(df['clarity'], categories=clarity_order, ordered=True)

    os.makedirs(os.path.dirname(CLEANED_DATA_PATH), exist_ok=True)
    df.to_csv(CLEANED_DATA_PATH, index=False)
    print(f"Cleaned dataset saved: {CLEANED_DATA_PATH} ({len(df):,} valid diamonds)")
    return df


def execute_hypothesis_tests(df):
    """Executes ANOVA, Welch's t-test, Tukey HSD, and Chi-Square test."""
    print("\n" + "=" * 60)
    print("STEP 3: STATISTICAL HYPOTHESIS TESTING EXECUTION")
    print("=" * 60)

    # -------------------------------------------------------------------------
    # TEST 1: One-Way ANOVA (Cut Grade vs. Price-per-Carat)
    # H0: Mean price_per_carat is equal across all 5 cut grades
    # H1: At least one cut grade differs significantly
    # -------------------------------------------------------------------------
    cut_groups = [group['price_per_carat'].values for _, group in df.groupby('cut', observed=False)]
    f_stat, anova_p = stats.f_oneway(*cut_groups)
    print(f"[TEST 1 - ANOVA] F-statistic: {f_stat:.4f}, p-value: {anova_p:.4e}")

    # Tukey HSD Post-Hoc Analysis
    tukey = pairwise_tukeyhsd(endog=df['price_per_carat'], groups=df['cut'], alpha=0.05)
    print("Tukey HSD Post-Hoc Comparison completed.")

    # -------------------------------------------------------------------------
    # TEST 2: Independent Two-Sample Welch's t-Test (Colorless vs. Near-Colorless)
    # H0: Mean price_per_carat of Colorless (D-F) == Near-Colorless (G-J)
    # H1: Mean price_per_carat differs significantly between color tiers
    # -------------------------------------------------------------------------
    colorless = df[df['color_tier'] == 'Colorless (D-F)']['price_per_carat']
    near_colorless = df[df['color_tier'] == 'Near-Colorless (G-J)']['price_per_carat']

    t_stat, ttest_p = stats.ttest_ind(colorless, near_colorless, equal_var=False)
    mean_diff = float(colorless.mean() - near_colorless.mean())
    se_diff = np.sqrt(colorless.var()/len(colorless) + near_colorless.var()/len(near_colorless))
    ci_lower = mean_diff - 1.96 * se_diff
    ci_upper = mean_diff + 1.96 * se_diff
    print(f"[TEST 2 - Welch's t-Test] t-stat: {t_stat:.4f}, p-value: {ttest_p:.4e}")
    print(f"  Mean Diff: ${mean_diff:.2f}, 95% CI: [${ci_lower:.2f}, ${ci_upper:.2f}]")

    # -------------------------------------------------------------------------
    # TEST 3: Chi-Square Test of Independence (Cut Grade vs. Clarity Grade)
    # H0: Cut grade and Clarity grade are independent
    # H1: Cut grade and Clarity grade are dependent
    # -------------------------------------------------------------------------
    contingency = pd.crosstab(df['cut'], df['clarity'])
    chi2, chi2_p, dof, expected = stats.chi2_contingency(contingency)
    
    # Calculate Cramer's V effect size
    n = contingency.sum().sum()
    min_dim = min(contingency.shape) - 1
    cramers_v = np.sqrt(chi2 / (n * min_dim))
    print(f"[TEST 3 - Chi-Square] Chi2: {chi2:.2f}, dof: {dof}, p-value: {chi2_p:.4e}, Cramer's V: {cramers_v:.4f}")

    # Standardized Pearson residuals: (O - E) / sqrt(E)
    std_residuals = (contingency - expected) / np.sqrt(expected)

    test_results = {
        'anova': {
            'f_stat': round(float(f_stat), 4),
            'p_value': float(anova_p),
            'reject_null': bool(anova_p < 0.05),
            'alpha': 0.05
        },
        'welch_ttest': {
            't_stat': round(float(t_stat), 4),
            'p_value': float(ttest_p),
            'colorless_mean': round(float(colorless.mean()), 2),
            'near_colorless_mean': round(float(near_colorless.mean()), 2),
            'mean_diff': round(mean_diff, 2),
            'ci_lower': round(ci_lower, 2),
            'ci_upper': round(ci_upper, 2),
            'reject_null': bool(ttest_p < 0.05)
        },
        'chi_square': {
            'chi2_stat': round(float(chi2), 2),
            'p_value': float(chi2_p),
            'dof': int(dof),
            'cramers_v': round(float(cramers_v), 4),
            'reject_null': bool(chi2_p < 0.05)
        }
    }

    return test_results, tukey, std_residuals, contingency


def generate_visualizations(df, test_results, tukey, std_residuals):
    """Generates 4 high-resolution statistical evidence charts."""
    print("\n" + "=" * 60)
    print("STEP 4: STATISTICAL VISUALIZATIONS GENERATION")
    print("=" * 60)
    os.makedirs(FIGURES_DIR, exist_ok=True)
    fig_paths = {}

    # -------------------------------------------------------------------------
    # FIGURE 1: ANOVA Cut Grade vs Price-per-Carat
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Subplot A: Boxplot with mean diamond markers
    cut_order = ['Fair', 'Good', 'Very Good', 'Premium', 'Ideal']
    sns.boxplot(data=df, x='cut', y='price_per_carat', order=cut_order, palette='Blues_r', ax=axes[0],
                showmeans=True, meanprops={"marker":"o", "markerfacecolor":"red", "markeredgecolor":"black", "markersize":"6"},
                hue='cut', legend=False)
    axes[0].set_title(f'Figure 1A: Price/Carat Distribution Across Cut Grades\n(One-Way ANOVA F={test_results["anova"]["f_stat"]:.2f}, p < 0.001)', 
                      fontsize=10.5, fontweight='bold')
    axes[0].set_ylabel('Price per Carat ($)')
    axes[0].set_xlabel('Diamond Cut Grade')
    axes[0].set_ylim(0, 15000)

    # Subplot B: Mean with 95% Confidence Intervals
    sns.pointplot(data=df, x='cut', y='price_per_carat', order=cut_order, color='#c0392b', capsize=0.15, err_kws={'linewidth': 2}, ax=axes[1])
    axes[1].set_title('Figure 1B: Group Means with 95% Confidence Intervals', fontsize=10.5, fontweight='bold')
    axes[1].set_ylabel('Mean Price per Carat ($)')
    axes[1].set_xlabel('Diamond Cut Grade')

    plt.tight_layout()
    f1_path = os.path.join(FIGURES_DIR, "fig1_anova_cut_vs_price_per_carat.png")
    plt.savefig(f1_path, dpi=160)
    plt.close()
    fig_paths['fig1'] = f1_path
    print(f"Generated: {f1_path}")

    # -------------------------------------------------------------------------
    # FIGURE 2: Welch's t-Test Comparison
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Subplot A: Dual KDE with shaded rejection areas
    sns.kdeplot(data=df[df['color_tier'] == 'Colorless (D-F)']['price_per_carat'], label='Colorless (D-F)', 
                color='#2980b9', fill=True, alpha=0.35, ax=axes[0])
    sns.kdeplot(data=df[df['color_tier'] == 'Near-Colorless (G-J)']['price_per_carat'], label='Near-Colorless (G-J)', 
                color='#e67e22', fill=True, alpha=0.35, ax=axes[0])
    axes[0].set_title(f"Figure 2A: Price/Carat Density by Color Tier\n(Welch's t={test_results['welch_ttest']['t_stat']:.2f}, p < 0.001)",
                      fontsize=10.5, fontweight='bold')
    axes[0].set_xlabel('Price per Carat ($)')
    axes[0].set_xlim(0, 15000)
    axes[0].legend(loc='upper right')

    # Subplot B: Mean Difference and 95% Confidence Interval Bar
    diff_val = test_results['welch_ttest']['mean_diff']
    ci_low = test_results['welch_ttest']['ci_lower']
    ci_high = test_results['welch_ttest']['ci_upper']
    
    axes[1].errorbar(x=[diff_val], y=[0], xerr=[[diff_val - ci_low], [ci_high - diff_val]], fmt='o', color='#c0392b',
                     ecolor='#2c3e50', elinewidth=2.5, capsize=8, markersize=8)
    axes[1].axvline(0, color='gray', linestyle='--', linewidth=1.5, label='Null Value (H0: Diff = 0)')
    axes[1].set_title(f'Figure 2B: Mean Difference (D-F vs G-J) & 95% CI\n[${ci_low:.1f}, ${ci_high:.1f}] (Rejects H0)',
                      fontsize=10.5, fontweight='bold')
    axes[1].set_xlabel('Difference in Mean Price/Carat ($)')
    axes[1].set_yticks([])
    axes[1].legend(loc='lower left')

    plt.tight_layout()
    f2_path = os.path.join(FIGURES_DIR, "fig2_welchs_ttest_color_comparison.png")
    plt.savefig(f2_path, dpi=160)
    plt.close()
    fig_paths['fig2'] = f2_path
    print(f"Generated: {f2_path}")

    # -------------------------------------------------------------------------
    # FIGURE 3: Tukey's HSD Pairwise Confidence Intervals
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5.5))
    tukey_data = pd.DataFrame(data=tukey._results_table.data[1:], columns=tukey._results_table.data[0])
    tukey_data['pair'] = tukey_data['group1'].astype(str) + " vs " + tukey_data['group2'].astype(str)
    
    # Plot pairwise intervals
    y_pos = range(len(tukey_data))
    ax.errorbar(tukey_data['meandiff'], y_pos, 
                xerr=[tukey_data['meandiff'] - tukey_data['lower'], tukey_data['upper'] - tukey_data['meandiff']],
                fmt='s', color='#2e4053', ecolor='#16a085', elinewidth=2, capsize=5, markersize=6)
    ax.axvline(0, color='#e74c3c', linestyle='--', linewidth=1.5, label='Zero Difference (No Effect)')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(tukey_data['pair'])
    ax.set_title("Figure 3: Tukey's HSD 95% Family-Wise Simultaneous Confidence Intervals for Cut Pairs", fontsize=11, fontweight='bold', pad=12)
    ax.set_xlabel('Difference in Mean Price per Carat ($)')
    ax.legend(loc='lower right')

    plt.tight_layout()
    f3_path = os.path.join(FIGURES_DIR, "fig3_tukey_hsd_pairwise_comparisons.png")
    plt.savefig(f3_path, dpi=160)
    plt.close()
    fig_paths['fig3'] = f3_path
    print(f"Generated: {f3_path}")

    # -------------------------------------------------------------------------
    # FIGURE 4: Chi-Square Residuals Heatmap
    # -------------------------------------------------------------------------
    plt.figure(figsize=(10, 5.5))
    sns.heatmap(std_residuals, annot=True, fmt='.1f', cmap='vlag', center=0, cbar_kws={'label': 'Std Pearson Residual (O - E)/√E'})
    plt.title(f'Figure 4: Chi-Square Test of Independence: Standardized Residuals\n(Chi2={test_results["chi_square"]["chi2_stat"]:.1f}, dof={test_results["chi_square"]["dof"]}, p < 0.001, Cramer\'s V={test_results["chi_square"]["cramers_v"]:.3f})',
              fontsize=11, fontweight='bold', pad=12)
    plt.xlabel('Clarity Grade')
    plt.ylabel('Cut Grade')
    plt.tight_layout()
    f4_path = os.path.join(FIGURES_DIR, "fig4_chisquare_cut_clarity_residuals.png")
    plt.savefig(f4_path, dpi=160)
    plt.close()
    fig_paths['fig4'] = f4_path
    print(f"Generated: {f4_path}")

    return fig_paths


def save_metrics(df, test_results):
    """Saves serialized results to json for document builder."""
    cut_means = df.groupby('cut', observed=False)['price_per_carat'].agg(['count', 'mean', 'std', 'median']).to_dict(orient='index')
    formatted_cut_means = {}
    for k, v in cut_means.items():
        formatted_cut_means[str(k)] = {
            'count': int(v['count']),
            'mean': round(float(v['mean']), 2),
            'std': round(float(v['std']), 2),
            'median': round(float(v['median']), 2)
        }

    full_metrics = {
        'total_records': len(df),
        'cut_means': formatted_cut_means,
        'test_results': test_results
    }

    with open(METRICS_PATH, 'w') as f:
        json.dump(full_metrics, f, indent=4)

    print(f"Metrics saved to: {METRICS_PATH}")
    return full_metrics


def main():
    df_raw = acquire_data()
    df_cleaned = clean_and_prepare(df_raw)
    test_results, tukey, std_residuals, contingency = execute_hypothesis_tests(df_cleaned)
    fig_paths = generate_visualizations(df_cleaned, test_results, tukey, std_residuals)
    full_metrics = save_metrics(df_cleaned, test_results)
    print("\n" + "=" * 60)
    print("HYPOTHESIS TESTING PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"ANOVA F: {test_results['anova']['f_stat']} | Welch's t: {test_results['welch_ttest']['t_stat']} | Chi2: {test_results['chi_square']['chi2_stat']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
