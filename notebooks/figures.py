"""House style and plotting helpers shared by the notebooks: Nord colours, Latin Modern Sans, figures at the report's sizes."""
import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D
from matplotlib.mlab import GaussianKDE
from matplotlib.patches import Patch, Rectangle
from IPython.display import display

ROOT = Path(__file__).resolve().parent.parent
palette = json.load(open(ROOT / "notebooks" / "nord.json"))
colours = dict(zip(["bach", "palestrina"], palette["categorical"]))
ink, muted, grid = (palette["roles"][k] for k in ("ink", "muted", "grid"))

# Figures are drawn at their printed size, so LaTeX includes them unscaled and the text stays 8-9 pt
COLUMN = (170 - 18 * 25.4 / 72.27) / 2 / 25.4   # one column of the report in inches: (A4 minus 2 cm margins, minus the 18 pt gap) / 2
PAGE = 170 / 25.4   # the full text width in inches, for figures across both columns (figure* in LaTeX)
for face in ["regular", "bold", "oblique"]:   # Latin Modern Sans, the font of the slides
    font_manager.fontManager.addfont(f"/usr/share/texmf/fonts/opentype/public/lm/lmsans10-{face}.otf")
plt.rcParams.update({"font.family": "Latin Modern Sans",
                     "font.size": 9, "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8})

FIGURES = ROOT / "tex" / "figures"   # read by the report and by the slides


def save(fig, name):
    """Save the figure as tex/figures/<name>.pdf, transparent, so it reads on the report's white page and on a light slide."""
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / f"{name}.pdf", transparent=True)


def boxes(table, columns, caption, stem):
    """One column per metric of `table`, one row per corpus: a density curve on a log axis with a box plot under it."""
    values = {(column, name): g[column] for column in columns for name, g in table.groupby("corpus")}
    logs = {k: np.log10(v) for k, v in values.items()}   # log units: density, whiskers and outliers as the axis shows them
    spans = {k: np.linspace(x.min(), x.max(), 200) for k, x in logs.items()}   # each curve stops at its own minimum and maximum
    # the estimator of a violin plot; density per decade x 10 = percent of files in a tenth of a decade
    densities = {k: 10 * GaussianKDE(x, "scott").evaluate(spans[k]) for k, x in logs.items()}
    top = max(d.max() for d in densities.values())
    fig, axes = plt.subplots(2, len(columns), figsize=(PAGE, 2.8), sharex="col", sharey=True)
    for col, (column, title) in enumerate(columns.items()):
        for ax, name in zip(axes[:, col], colours):
            x, median, c = logs[column, name], values[column, name].median(), colours[name]
            ax.fill_between(spans[column, name], densities[column, name], color=to_rgba(c, 0.35), linewidth=0)
            ax.boxplot(x, positions=[-0.2 * top], widths=0.1 * top, orientation="horizontal", patch_artist=True, manage_ticks=False,
                       showcaps=False, boxprops=dict(facecolor="white", edgecolor=c), whiskerprops=dict(color=c),
                       medianprops=dict(color=c, linewidth=2),
                       flierprops=dict(marker="o", markersize=1.8, markerfacecolor="none", markeredgecolor=c, markeredgewidth=0.5))
            ax.text(np.log10(median), -0.3 * top, f"{median:g}", ha="center", va="top", fontsize=7, color=muted)
            ax.set_ylim(-0.48 * top, 1.05 * top)
            ax.set_yticks(np.arange(0, top, 10))
            ax.yaxis.set_major_formatter(lambda v, _: f"{v:g}%")
            ax.grid(color=to_rgba(grid, 0.6), linewidth=0.4)   # faint grid both ways
            ax.axhline(0, color=grid, linewidth=0.6)   # the baseline of the curve, a little stronger
            ax.set_axisbelow(True)
            ax.spines[["top", "right", "left"]].set_visible(False)
            ax.spines["bottom"].set_color(muted)
            ax.tick_params(colors=muted, length=0)
        lo, hi = table[column].min(), table[column].max()
        ticks = [m * 10 ** e for e in range(6) for m in (1, 3) if lo <= m * 10 ** e <= hi]
        axes[1, col].set_xticks(np.log10(ticks), [f"{t:g}" for t in ticks])
        axes[1, col].set_xlabel(title, color=muted)   # the metric under its axis; the caption replaces a title
        axes[0, col].spines["bottom"].set_visible(False)   # the two rows share the x axis drawn under the bottom one
    fig.supylabel("files per tenth of a decade", x=0.01, color=muted, fontsize=9)
    axes[0, 0].legend(handles=[Patch(facecolor=to_rgba(colours[name], 0.35), edgecolor=colours[name], label=name.capitalize()) for name in colours],
                      loc="upper right", frameon=False, labelcolor=ink, handlelength=0.8, handleheight=0.8, handletextpad=0.4, borderaxespad=0)
    fig.tight_layout(pad=0.3, rect=(0.03, 0, 1, 1))   # a strip on the left for the shared y label
    for left, right in zip(axes[0], axes[0][1:]):   # a thin rule halfway between neighbouring columns
        x = (left.get_position().x1 + right.get_position().x0) / 2
        fig.add_artist(Line2D([x, x], [axes[1, 0].get_position().y0, axes[0, 0].get_position().y1], color=grid, linewidth=0.5))
    save(fig, stem)
    plt.show()
    print(caption)
    display(table.groupby("corpus")[list(columns)].agg(["mean", "std", "min", "median", "max"]).stack(level=0).round(1))


def stacked(shares, xlabel, caption, labels=None, *, stem):
    """One 100% bar per corpus, with a key of every block's colour; `shares` has one row per corpus and one column per block."""
    shades = np.linspace(1, 0.25, shares.shape[1])   # blocks come from the largest value to the smallest: darker always means more
    n = shares.shape[1]
    PITCH = max(1.2, 0.27 * max(len(str(column)) for column in shares.columns))   # key columns spaced by their longest label
    fig, (top, ax) = plt.subplots(2, 1, figsize=(COLUMN, 1.35), height_ratios=[0.5, 1])
    for r, name in enumerate(colours):   # the key: one row per corpus, one column per block, each swatch the colour of its block
        for c, alpha in enumerate(shades):
            top.add_patch(Rectangle((c * PITCH, r), PITCH - 0.2, 0.72, facecolor=to_rgba(colours[name], alpha), edgecolor="none"))
        top.text(-0.15, r + 0.36, name.capitalize(), ha="right", va="center", fontsize=7, color=ink)
    for c, column in enumerate(shares.columns):
        top.text(c * PITCH + (PITCH - 0.2) / 2, -0.12, str(column), ha="center", va="bottom", fontsize=6.5, color=ink)
    top.set_xlim(n * PITCH + 0.1 - 19, n * PITCH + 0.1)   # the same scale in every figure, the key flush right
    top.set_ylim(2, -0.75)
    top.axis("off")
    for y, name in zip([1, 0], colours):
        left = 0
        for column, alpha in zip(shares.columns, shades):
            w = shares.loc[name, column]
            ax.barh(y, w, left=left, height=0.65, color=to_rgba(colours[name], alpha), edgecolor="white", linewidth=0.8)
            if w >= 8:   # narrower blocks stay unlabelled; the key gives their colour, the table below their value
                text = column if labels is None else labels.loc[name, column]
                ax.text(left + w / 2, y, f"{text}\n{w:.1f}%", ha="center", va="center", fontsize=6.5,
                        color="white" if alpha >= 0.7 else ink, linespacing=1.0)
            left += w
    ax.set_yticks([])   # Bach on top, Palestrina below, as in the key
    ax.set_ylim(-0.4, 1.4)
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:g}%")
    ax.set_xlabel(xlabel, color=muted)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(muted)
    ax.tick_params(colors=muted, length=0)
    fig.tight_layout(pad=0.3, h_pad=0.2)
    save(fig, stem)
    plt.show()
    print(caption)
