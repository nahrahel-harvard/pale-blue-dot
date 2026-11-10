# The Stellar Graveyard: interactive demo (project 18)

A beginner's interactive tour of every black-hole and neutron-star merger in the
LIGO-Virgo-KAGRA catalog: a merger simulator you can hear, the "graveyard" scatter plot with
tooltips and a replay of ten years of discoveries, mass histograms, the detection timeline,
a distance chart, a pair-instability "forbidden zone" slider, a quiz, a searchable data table
and a glossary (every dotted-underlined word has a tooltip).

## Files

- `stellar_graveyard.html`: the page (HTML, CSS and JavaScript; charts use D3 from cdnjs).
- `graveyard_data.js`: the catalog data the page reads. Made by the script below; don't edit it by hand.
- `make_demo_data.py`: rebuilds `graveyard_data.js` from the GWOSC files cached in `data/`.

## Open it

Open `stellar_graveyard.html` in a web browser, with `graveyard_data.js` in the same folder.
It needs an internet connection the first time (for the D3 charting library and the fonts).

## Rebuild the data

From the top folder of the repo:

```bash
python3 demo/make_demo_data.py
```

## Data source

LIGO Scientific Collaboration, Virgo Collaboration and KAGRA Collaboration, Gravitational-Wave
Transient Catalog (cumulative, GWTC-1 through GWTC-5.0), from the Gravitational Wave Open Science
Center: https://gwosc.org/eventapi/csv/GWTC/ . Observing-run dates: https://gwosc.org/api/v2/runs .
Released under CC BY 4.0. "This research has made use of data or software obtained from the
Gravitational Wave Open Science Center (gwosc.org), a service of the LIGO Scientific Collaboration,
the Virgo Collaboration, and KAGRA." Full citation list: https://gwosc.org/acknowledgement/

The merger simulator is an illustration from the leading-order chirp formula, not detector data.
