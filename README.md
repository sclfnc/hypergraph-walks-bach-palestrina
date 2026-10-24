# Higher-Order Interactions in Musical Style

**Imitating Bach and Palestrina with hypergraph walks.** Final project for the course *Advanced Laboratory of Complex Network Analysis*, MSc in Data Science and Business Informatics, University of Pisa, academic year 2026/27. Author: Francesco Secoli.

- **Question:** can a hypergraph walk imitate a musical style, and which parts does it need?
- **Corpora:** 352 Bach chorales and 1,179 movements of Palestrina's masses, from the music21 corpus.
- **Status:** the corpus pipeline (notebooks 00 to 03) is complete; the model and the report are in progress.

## Repository structure

```
.
├── LICENSE                 GPL-3.0
├── README.md
├── environment.yml         the conda environment of the notebooks (alcna)
├── notebooks/              one notebook per step, run in order
│   ├── README.md                what each notebook reads and writes, and how to run it
│   ├── 00_understanding.ipynb   downloads the two corpora from music21 and describes them
│   ├── 01_filtering.ipynb       filters the files and labels them (key, tonal type, transposition, copies)
│   ├── 02_corpus.ipynb          repeats, weights, groups and folds of the corpus the model counts
│   ├── 03_description.ipynb     length, voices, rhythm and texture of the filtered corpus
│   ├── 04_hypergraph.ipynb      from the corpus to the hypergraph (a draft: the figure of the hyperedge shapes)
│   ├── figures.py               the house style and plotting helpers that 00, 03 and 04 share
│   └── nord.json                plot colours (Nord palette)
└── tex/                    everything LaTeX
    ├── references.bib      the one bibliography, shared by report and slides
    ├── report/             project report, from the course template (main.tex, abstract.tex, sections/)
    └── slides/             SimplePlusNord theme, and one folder per presentation (date and purpose)
```

The data are not in the repository: `00_understanding` and `01_filtering` download them into `data/`. The figures the notebooks draw go to `tex/figures/`, also outside the repository.

## Run the notebooks

```bash
conda env create -f environment.yml
conda activate alcna
```

Then follow [notebooks/README.md](notebooks/README.md).

## Build the report

From `tex/report/`:

```bash
latexmk -lualatex main.tex
```

## AI assistance

[Claude Code](https://claude.com/product/claude-code), by Anthropic, assisted with the code, the notebooks, the editing of the report and the slides, and the literature review.

## License

Code and notebooks: GNU General Public License v3.0, see [LICENSE](LICENSE). Report and slides: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
