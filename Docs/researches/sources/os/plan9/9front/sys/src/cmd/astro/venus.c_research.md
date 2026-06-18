# File Research: sources/os/plan9/9front/sys/src/cmd/astro/venus.c

Computes Venus’s apparent position.

Important behavior:
- Sets Venus mean orbital elements and perturbing planet anomalies.
- Applies long-period mean anomaly terms.
- Uses `venfp`/`vencp` through `cosadd` for longitude, latitude, and radius perturbations.
- Computes phase-angle magnitude and semi-diameter, then calls `helio()` and `geo()`.

This is the table-driven Venus counterpart to Mercury.
