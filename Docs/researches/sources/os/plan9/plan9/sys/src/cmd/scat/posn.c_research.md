# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/posn.c

Converts sky coordinates to DSS plate x/y positions.

Key functions:
- `traneqstd` converts RA/Dec to standard coordinates relative to the plate center.
- `ppoinv` applies the simpler PPO inverse transform.
- `amdinv` iteratively solves AMD polynomial plate equations with Newton-style updates.
- `xypos` selects AMD or PPO conversion based on `Header.amdflag`.

Behavior notes:
- AMD uses many header polynomial parameters for X and Y, plus magnitude/color terms.
- Iteration is bounded by `max_iterations` and stops on a small tolerance.
- Output is stored in `Header.x`, `Header.y`, `Header.xi`, and `Header.eta`.
