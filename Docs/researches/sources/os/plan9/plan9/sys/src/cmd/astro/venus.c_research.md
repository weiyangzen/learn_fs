# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/venus.c

Computes Venus ephemeris with perturbation series.

Key points:
- Builds Venus orbital elements and mean anomalies for perturbing planets.
- Applies long-period anomaly terms.
- Solves Kepler’s equation.
- Uses `venfp`/`vencp` for longitude, latitude, and log-radius perturbations.
- Computes phase magnitude and semidiameter, then calls `helio` and `geo`.

Dependencies:
- Uses coefficient table in `venust.c`.

Notable behavior:
- Magnitude includes a cubic phase-angle term.
