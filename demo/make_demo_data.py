"""Build demo/graveyard_data.js, the data file that demo/stellar_graveyard.html reads.

Run it from the top folder of the repo:

    python3 demo/make_demo_data.py

It uses the two files that notebooks/18_stellar_graveyard.ipynb saves in data/ (and downloads them
from gwosc.org if they're missing). It keeps only the columns the page needs and adds:
  - the detection date, converted from GPS time
  - the observing run each event belongs to
  - the light-travel time ("lookback time"), worked out from the redshift
    using the Planck 2015 cosmology (the same one the LIGO-Virgo-KAGRA catalogs use)
"""
import json
from datetime import date
from pathlib import Path

import pandas as pd
import requests
from astropy.cosmology import Planck15
from astropy.time import Time

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
OUT = ROOT / 'demo' / 'graveyard_data.js'
CATALOG_URL = 'https://gwosc.org/eventapi/csv/GWTC/'
RUNS_URL = 'https://gwosc.org/api/v2/runs'
RUN_NAMES = ['O1', 'O2', 'O3a', 'O3b', 'O4a', 'O4b']


def download_once(url, filename):
    # Download a file into data/ the first time. After that, just reuse the saved copy.
    path = DATA / filename
    if not path.exists():
        DATA.mkdir(exist_ok=True)
        response = requests.get(url, timeout=60)
        response.raise_for_status()   # stop with a clear error if the download failed
        path.write_bytes(response.content)
        print('Downloaded', url)
    return path


def gps_to_iso(gps):
    # GPS seconds -> 'YYYY-MM-DDTHH:MM:SSZ' (UTC), a date format JavaScript understands
    return Time(float(gps), format='gps').utc.strftime('%Y-%m-%dT%H:%M:%SZ')


def value_and_range(row, column, digits):
    # [median, low end, high end] of the 90% range, or None if the catalog has no value
    middle = row[column]
    if pd.isna(middle):
        return None
    low, high = row.get(column + '_lower'), row.get(column + '_upper')
    low = middle if pd.isna(low) else middle + low      # the catalog stores the range as offsets
    high = middle if pd.isna(high) else middle + high
    return [round(float(v), digits) for v in (middle, low, high)]


def plain(value, digits):
    # A rounded number, or None when the catalog leaves it blank
    return None if pd.isna(value) else round(float(value), digits)


catalog = pd.read_csv(download_once(CATALOG_URL, 'gwtc_cumulative.csv'))
runs = pd.DataFrame(json.loads(download_once(RUNS_URL, 'gwosc_runs.json').read_text())['results'])
runs = runs[runs['name'].isin(RUN_NAMES)].reset_index(drop=True)

events = []
for _, row in catalog.sort_values('GPS').iterrows():
    run = runs.loc[(runs['gps_start'] <= row['GPS']) & (row['GPS'] <= runs['gps_end']), 'name']
    redshift = value_and_range(row, 'redshift', 4)
    lookback = None
    if redshift:   # light-travel time in billions of years, for the median and both ends of the range
        lookback = [round(float(Planck15.lookback_time(max(z, 0)).to_value('Gyr')), 2) for z in redshift]
    events.append({
        'name': row['commonName'],
        'catalog': row['catalog.shortName'].replace('-confident', ''),
        'date': gps_to_iso(row['GPS']),
        'run': run.iloc[0] if len(run) else None,
        'm1': value_and_range(row, 'mass_1_source', 2),         # heavier object [Msun]
        'm2': value_and_range(row, 'mass_2_source', 2),         # lighter object [Msun]
        'mf': value_and_range(row, 'final_mass_source', 2),     # black hole left afterwards [Msun]
        'mc': value_and_range(row, 'chirp_mass_source', 2),     # chirp mass [Msun]
        'dist': value_and_range(row, 'luminosity_distance', 0),  # [Mpc]
        'z': redshift,
        'lookback': lookback,                                   # [billion years]
        'chi': value_and_range(row, 'chi_eff', 2),              # effective spin
        'pastro': plain(row['p_astro'], 3),                     # chance it's a real astrophysical signal
        'far': plain(row['far'], 8),                            # false alarms per year
        'snr': plain(row['network_matched_filter_snr'], 1),     # signal-to-noise ratio
    })

run_list = [{
    'name': r['name'],
    'start': gps_to_iso(r['gps_start']),
    'end': gps_to_iso(r['gps_end']),
    'detectors': r['detectors'],
    'events': int(catalog['GPS'].between(r['gps_start'], r['gps_end']).sum()),
} for _, r in runs.iterrows()]

payload = {
    'made': date.fromtimestamp((DATA / 'gwtc_cumulative.csv').stat().st_mtime).isoformat(),
    'sources': {'catalog': CATALOG_URL, 'runs': RUNS_URL},
    'events': events,
    'runs': run_list,
}
OUT.write_text('// Made by demo/make_demo_data.py from public GWOSC data (gwosc.org). Rebuild it; do not edit by hand.\n'
               'window.GRAVEYARD = ' + json.dumps(payload, separators=(',', ':')) + ';\n')
print(f'Wrote {OUT} ({OUT.stat().st_size / 1000:.0f} kB): {len(events)} events, {len(run_list)} observing runs')
