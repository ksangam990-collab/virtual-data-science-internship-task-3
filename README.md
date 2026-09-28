# Virtual Data Science with Python Apprentice Intern
## Week 3: Statistical Analysis and Hypothesis Testing in Python

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![SciPy](https://img.shields.io/badge/SciPy-Hypothesis%20Testing-195f9c.svg)
![Statsmodels](https://img.shields.io/badge/Statsmodels-ANOVA%20%26%20Post--Hoc-003366.svg)
![Status](https://img.shields.io/badge/Milestone-Week%203%20Completed-brightgreen.svg)

---

### 🔬 Empirical Study: Gemological Valuation Premia & Quality Independence
This repository contains the official Week 3 deliverables for **ksangam990** under the **Virtual Data Science with Python Apprentice Internship**. This milestone emphasizes the formulation, rigorous mathematical execution, and validation/refutation of real-world hypotheses using parametric and non-parametric statistical methods.

Investigating **53,775 verified diamonds**, the project tests three core market hypotheses:
1. **Hypothesis 1 (One-Way ANOVA):** Does cut craftsmanship significantly influence unit valuation (price-per-carat)?
2. **Hypothesis 2 (Two-Sample Welch's t-Test):** Do colorless diamonds command a statistically significant unit price premium over near-colorless stones?
3. **Hypothesis 3 (Chi-Square Independence Test):** Are cut grade craftsmanship and natural clarity ratings statistically independent?

---

### 📁 Directory Layout
```text
diamonds-statistical-hypothesis-ksangam990/
├── analysis_pipeline.py                    # Complete statistical testing & visualization pipeline
├── generate_docx_report.py                 # Automated Word document report generator
├── Week3_Diamonds_Statistical_Hypothesis_Testing_Report.docx # Official deliverable (390 KB)
├── requirements.txt                        # Python dependencies
├── .gitignore                              # Git exclusion rules
├── README.md                               # Project documentation & statistical evidence
├── data/
│   ├── raw/
│   │   └── diamonds_raw.csv                # Raw dataset (53,940 diamonds)
│   └── processed/
│       ├── diamonds_cleaned.csv            # Cleaned dataset (53,775 valid records)
│       └── hypothesis_testing_metrics.json # Serialized statistical test metrics
└── figures/
    ├── fig1_anova_cut_vs_price_per_carat.png # One-Way ANOVA boxplots & 95% CI error bars
    ├── fig2_welchs_ttest_color_comparison.png # Welch's t-test KDE & mean difference CI
    ├── fig3_tukey_hsd_pairwise_comparisons.png # Tukey's HSD simultaneous pairwise intervals
    └── fig4_chisquare_cut_clarity_residuals.png # Chi-square standardized Pearson residuals heatmap
```

---

### 📊 Summary of Hypothesis Test Results

| Test Type | Null Hypothesis ($H_0$) | Test Statistic | p-Value | Statistical Decision |
| :--- | :--- | :--- | :--- | :--- |
| **One-Way ANOVA** | Equal mean price/carat across 5 cut grades | $F = 61.68$ | $4.35 \times 10^{-52}$ | **REJECT $H_0$** (Significant Cut Variance) |
| **Welch's t-Test** | Equal mean price/carat between Colorless & Near-Colorless | $t = -4.88$ | $1.05 \times 10^{-6}$ | **REJECT $H_0$** (95% CI: [-$119.02, -$50.83]) |
| **Chi-Square ($\chi^2$)** | Independence between Cut Grade and Clarity Grade | $\chi^2 = 4,373.38$ | $< 0.001$ | **REJECT $H_0$** (Cramer's V = 0.143, Dependent) |

---

### 🚀 Getting Started

```bash
# 1. Clone repository
git clone https://github.com/ksangam990-collab/virtual-data-science-internship-task-3.git
cd virtual-data-science-internship-task-3

# 2. Install dependencies
pip install -r requirements.txt

# 3. Execute statistical tests & generate charts
python analysis_pipeline.py

# 4. Compile Word Document Report
python generate_docx_report.py
```

---
**Candidate:** ksangam990  
**Internship:** Virtual Data Science with Python Apprentice Intern  
**Adherence to Workload:** 32 Hours Logged  
