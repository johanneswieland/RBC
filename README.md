# Economics 210A: Business Cycles

Lecture notes with runnable code. **Read them as a website: <https://johanneswieland.github.io/RBC/>**

Every number and figure in the lectures is produced by the code next to it, so you can rerun it, change the assumptions, and see how the results are obtained.

| # | Lecture | Notebook |
|---|---------|----------|
| 1 | Business cycle facts | [`lectures/01_business_cycle_facts.ipynb`](lectures/01_business_cycle_facts.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/johanneswieland/RBC/blob/main/lectures/01_business_cycle_facts.ipynb) |
| 2 | The basic RBC model in continuous time | [`lectures/02_rbc_continuous_time.ipynb`](lectures/02_rbc_continuous_time.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/johanneswieland/RBC/blob/main/lectures/02_rbc_continuous_time.ipynb) |
| 3 | Comparative statics: phase diagrams and shocks | [`lectures/03_comparative_statics.ipynb`](lectures/03_comparative_statics.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/johanneswieland/RBC/blob/main/lectures/03_comparative_statics.ipynb) |

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

## Repository layout

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
jupyter-book start
```

