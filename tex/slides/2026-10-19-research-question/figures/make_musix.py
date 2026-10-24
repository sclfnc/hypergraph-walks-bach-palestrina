"""The first two bars of Bach chorale 41 and of Palestrina's Credo as MusiXTeX code, four voices on four staves each, same size
and same width, for the slide "Which data?". Reads the notes from the music21 corpus and writes figures/chorale_musix.tex and
figures/palestrina_musix.tex, to be \\input inside a frame. The staves of MusiXTeX count from the bottom: bass is instrument 1.
Needs music21 in the env `gen`. Run from the folder of the talk. No musixflx pass is needed: the spacing is set here."""
from fractions import Fraction as F
from music21 import corpus

WIDTH_PT = 115    # the scalable space of both excerpts, so that they have the same width
STEP = {"C": 0, "D": 1, "E": 2, "F": 3, "G": 4, "A": 5, "B": 6}
BOTTOM = {"treble": 4 * 7 + 2, "treble8vb": 4 * 7 + 2, "bass": 2 * 7 + 4}    # lowest line: E4, E4, G2
CLEF = {"treble": r"\treble", "treble8vb": r"\treble", "bass": r"\bass"}
SPACING = {F(1, 4): ("notes", 2), F(1, 2): ("Notes", 3), F(3, 4): ("Notesp", 3.5), F(1): ("NOtes", 4), F(3, 2): ("NOtesp", 4.5),
           F(2): ("NOTes", 5), F(3): ("NOTesp", 5.5), F(4): ("NOTEs", 6)}
NOTE = {F(4): "zw", F(2): "zh", F(1): "zq", F(1, 2): "zc", F(1, 4): "zcc"}       # stem direction is added: u or l
REST = {F(4): r"\pause", F(2): r"\hpause", F(1): r"\qp"}
ORDER = ["S", "A", "T", "B"]                                                      # top to bottom
NAMES = {"S": "Soprano", "A": "Alto", "T": "Tenor", "B": "Bass"}
CLEFS = {"S": "treble", "A": "treble", "T": "treble8vb", "B": "bass"}

def dia(p): return p.octave * 7 + STEP[p.step]

def events(part, first, last):
    """(onset, duration, pitch or None) of the notes and rests of the bars first..last, in quarter notes."""
    stream = part.measures(first, last).flatten().notesAndRests
    return [(F(n.offset).limit_denominator(16), F(n.quarterLength).limit_denominator(16), n.pitch if n.isNote else None) for n in stream]

def excerpt(parts, first, last, meter, signature, name):
    voices = {v: events(p, first, last) for v, p in zip(ORDER, parts)}
    assert all(v[0][0] == 0 for v in voices.values())
    bar = {"4/4": F(4), "4/2": F(8)}[meter]; end = bar * (last - first + 1)
    assert all(sum(d for _, d, _ in v) == end for v in voices.values()), "the voices do not end together"
    onsets = sorted({t for v in voices.values() for t, _, _ in v}); onsets.append(end)
    barlines = {bar * k for k in range(1, last - first + 1)}
    scalable = sum(SPACING[b - a][1] for a, b in zip(onsets, onsets[1:]))
    lines = [r"{\smallmusicsize\elemskip=%.2fpt" % (WIDTH_PT / scalable), r"\begin{music}", r"\parindent12mm\nobarnumbers",
             r"\instrumentnumber{4}"]
    for i, v in enumerate(reversed(ORDER), 1):                                    # instrument 1 is the bottom one
        lines.append(r"\setstaffs%d1\setclef%d{%s}\setname%d{\scriptsize %s}" % (i, i, "0" if CLEFS[v] != "bass" else "6", i, NAMES[v]))
        if CLEFS[v] == "treble8vb": lines.append(r"\setclefsymbol%d{\treblelowoct}" % i)
    lines.append(r"\generalsignature{%d}\generalmeter{\meterfrac%s}" % (signature, meter.replace("/", "")))
    lines.append(r"\startextract")
    for a, b in zip(onsets, onsets[1:]):
        fields = []
        for v in reversed(ORDER):
            hit = [(d, p) for t, d, p in voices[v] if t == a]
            if not hit: fields.append(""); continue
            d, p = hit[0]
            if p is None: fields.append(r"\rlap{%s}" % REST[d]); continue
            pos = dia(p) + (7 if CLEFS[v] == "treble8vb" else 0) - BOTTOM[CLEFS[v]]
            assert -9 <= pos <= 18
            dotted = d in (F(3), F(3, 2))
            stem = "" if d == F(4) else ("u" if pos < 4 else "l")
            fields.append(r"\%s%s%s{%d}" % (NOTE[d] if not dotted else "zh", stem, "p" if dotted else "", pos))
        lines.append(r"\%s %s\sk\en%s" % (SPACING[b - a][0], "&".join(fields), r"\bar" if b in barlines else ""))
    lines += [r"\zendextract", r"\end{music}}"]
    open("figures/%s_musix.tex" % name, "w").write("\n".join(lines) + "\n")
    print(name, ":", len(onsets) - 1, "groups, scalable space", scalable, "elemskip %.2f pt" % (WIDTH_PT / scalable))

chorale = [x for x in corpus.chorales.Iterator(1, 41)][40]
assert chorale.metadata.title.startswith("Was mein Gott will")
excerpt(chorale.parts, 1, 2, "4/4", 0, "chorale")
credo = corpus.parse("palestrina/Credo_89_a.krn")
assert len(credo.parts) == 4
excerpt(credo.parts, 1, 2, "4/2", -1, "palestrina")
