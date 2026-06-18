# File Research: sources/os/plan9/9front/sys/src/cmd/scat/posn.c

Purpose: Converts celestial coordinates into DSS plate pixel positions.

Key routines:
- `traneqstd`: converts RA/Dec to standard tangent-plane coordinates `xi` and `eta`.
- `ppoinv`: applies linear PPO plate solution and converts microns to pixels.
- `amdinv`: applies AMD polynomial plate model using Newton iteration to invert from standard coordinates to plate coordinates.
- `xypos`: dispatches to AMD or PPO based on `Header.amdflag`.

Integration: Used by `image.c` after `getheader` to locate requested RA/Dec on a selected DSS plate.

Risks:
- `amdinv` uses fixed 50-iteration Newton solve and does not explicitly report non-convergence.
- Polynomial terms depend on header coefficients and plate scale units.
