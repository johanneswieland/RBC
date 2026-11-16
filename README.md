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

## Problem Set

Each lecture comes with a set of questions. I highly recommend you do all of them. The graded problem set consists of a subset:
1. Lecture 1, Q6
2. Lecture 2, Q2
3. Lecture 3, Q2
4. Lecture 4, Q3 & Q5

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

