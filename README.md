# Economics 210A: Real Business Cycles

The course is a brief overview of the Real Business Cycle framework. This framework forms the backbone of modern business cycle analysis as a minimal model of short-run fluctuations that is consistent with optimizing behavior and rational expectations. The model itself is obviously unrealistic but by studying it we will be able to better understand more realistic models that build on it. It is also in some respect remarkably successful at matching certain aspects of the data and we will work through the reasons for this success. An outlines of the themes we cover is below.

# Lectures

Monday, Wednesday: 10:30-11:50am, Malk Hall 5xx

| # | Lecture | Notebook |
|---|---------|----------|
| 1 | Business cycle facts | [`lectures/01_business_cycle_facts.ipynb`](lectures/01_business_cycle_facts.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/johanneswieland/RBC/blob/main/lectures/01_business_cycle_facts.ipynb) |
| 2 | The basic RBC model in continuous time | [`lectures/02_rbc_continuous_time.ipynb`](lectures/02_rbc_continuous_time.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/johanneswieland/RBC/blob/main/lectures/02_rbc_continuous_time.ipynb) |
| 3 | Comparative statics: phase diagrams and shocks | [`lectures/03_comparative_statics.ipynb`](lectures/03_comparative_statics.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/johanneswieland/RBC/blob/main/lectures/03_comparative_statics.ipynb) |
| 4 | Quantitative validity of the RBC model | [`lectures/04_quantitative_validity.ipynb`](lectures/04_quantitative_validity.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/johanneswieland/RBC/blob/main/lectures/04_quantitative_validity.ipynb) |

**Read them as a website: <https://johanneswieland.github.io/RBC/>**

## Readings

Starred readings (\*) are required; the others are recommended.

**Business cycle facts** (Lecture 1)

- \* King, Robert G. and Sergio T. Rebelo (1999). "[Resuscitating Real Business Cycles](https://doi.org/10.1016/S1574-0048%2899%2910022-3)." In *Handbook of Macroeconomics* 1B: 927–1007.
- Stock, James H. and Mark W. Watson (1999). "[Business Cycle Fluctuations in U.S. Macroeconomic Time Series](https://doi.org/10.1016/S1574-0048%2899%2901004-6)." In *Handbook of Macroeconomics* 1A: 3–64.

**Real business cycle model: review, criticisms, and business cycle accounting** (Lectures 2–4)

- \* King, Robert G. and Sergio T. Rebelo (1999). "[Resuscitating Real Business Cycles](https://doi.org/10.1016/S1574-0048%2899%2910022-3)." In *Handbook of Macroeconomics* 1B: 927–1007.
- \* Prescott, Edward C. (1986). "[Theory Ahead of Business Cycle Measurement](https://www.minneapolisfed.org/research/quarterly-review/theory-ahead-of-business-cycle-measurement)." *Federal Reserve Bank of Minneapolis Quarterly Review* 10(4): 9–22.
- \* Summers, Lawrence H. (1986). "[Some Skeptical Observations on Real Business Cycle Theory](https://www.minneapolisfed.org/research/quarterly-review/some-skeptical-observations-on-real-business-cycle-theory)." *Federal Reserve Bank of Minneapolis Quarterly Review* 10(4): 23–27.
- \* Prescott, Edward C. (1986). "[Response to a Skeptic](https://www.minneapolisfed.org/research/quarterly-review/response-to-a-skeptic)." *Federal Reserve Bank of Minneapolis Quarterly Review* 10(4): 28–33.
- Chetty, Raj, Adam Guren, Day Manoli, and Andrea Weber (2013). "[Does Indivisible Labor Explain the Difference between Micro and Macro Elasticities? A Meta-Analysis of Extensive Margin Elasticities](https://doi.org/10.1086/669170)." *NBER Macroeconomics Annual* 27: 1–56.
- Galí, Jordi (1999). "[Technology, Employment, and the Business Cycle: Do Technology Shocks Explain Aggregate Fluctuations?](https://doi.org/10.1257/aer.89.1.249)" *American Economic Review* 89(1): 249–271.
- Basu, Susanto, John G. Fernald, and Miles S. Kimball (2006). "[Are Technology Improvements Contractionary?](https://doi.org/10.1257/aer.96.5.1418)" *American Economic Review* 96(5): 1418–1448.
- Rotemberg, Julio J. and Michael Woodford (1996). "[Real-Business-Cycle Models and the Forecastable Movements in Output, Hours, and Consumption](https://www.jstor.org/stable/2118256)." *American Economic Review* 86(1): 71–89.
- Galí, Jordi, Mark Gertler, and J. David López-Salido (2007). "[Markups, Gaps, and the Welfare Costs of Business Fluctuations](https://doi.org/10.1162/rest.89.1.44)." *Review of Economics and Statistics* 89(1): 44–59.
- Chari, V. V., Patrick J. Kehoe, and Ellen R. McGrattan (2007). "[Business Cycle Accounting](https://doi.org/10.1111/j.1468-0262.2007.00768.x)." *Econometrica* 75(3): 781–836.
- Shimer, Robert (2009). "[Convergence in Macroeconomics: The Labor Wedge](https://doi.org/10.1257/mac.1.1.280)." *American Economic Journal: Macroeconomics* 1(1): 280–297.
- Bils, Mark, Peter J. Klenow, and Benjamin A. Malin (2018). "[Resurrecting the Role of the Product Market Wedge in Recessions](https://doi.org/10.1257/aer.20151260)." *American Economic Review* 108(4–5): 1118–1146.

## Running the notebooks

**In the browser (no installation):** click the *Open in Colab* badge.

**Locally:**
```bash
git clone https://github.com/johanneswieland/RBC.git
cd RBC
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

<!-- ## Repository layout

```
lectures/   one notebook per lecture (derivations + code + output)
code/       reusable Python modules imported by the notebooks
data/       snapshot of the downloaded data, used if a download fails
```

Data are downloaded at run time from [FRED](https://fred.stlouisfed.org) and John Fernald's [quarterly TFP database](https://www.frbsf.org/research-and-insights/data-and-indicators/total-factor-productivity-tfp/). No API key is needed.

## Building the website locally

The website is a [Jupyter Book](https://jupyterbook.org) built from the committed notebooks (configuration in `myst.yml`). It is rebuilt and published to GitHub Pages automatically on every push to `main`. To preview it locally (requires Node.js):
```bash
pip install "jupyter-book>=2"
jupyter-book start -->
```

