# Notebooks

Run them in order, with the `alcna` kernel (`../environment.yml`). Each one reads the table of the one before from `../data/interim/` and writes its own.

| Notebook | Reads | Writes |
|---|---|---|
| `00_understanding.ipynb` | the music21 corpus on GitHub (tag `v10.5.0`) | `data/raw/bach/`, `data/raw/palestrina/`, `data/interim/00_pieces.csv`, `tex/figures/00_*.pdf` |
| `01_filtering.ipynb` | `00_pieces.csv`; When in Rome on GitHub (fixed commit) | `data/raw/when_in_rome/`, `data/interim/01_corpus.csv` |
| `02_corpus.ipynb` | `01_corpus.csv` | `data/interim/02_corpus.csv` |
| `03_description.ipynb` | `00_pieces.csv`, `01_corpus.csv` | `tex/figures/03_*.pdf` |

`nord.json` holds the plot colours; `figures.py` the house style and the plotting helpers that 00 and 03 share.

The notebooks are kept without outputs. To run one headless and keep its outputs elsewhere, from this folder:

```bash
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.kernel_name=alcna --output-dir <folder> 01_filtering.ipynb
```

`alcna` has no `nbconvert`: run the command from an environment that has it. On a warm cache, 00 takes about 35 s, 01 about 50 s, 02 about 20 s, 03 about 10 s.
