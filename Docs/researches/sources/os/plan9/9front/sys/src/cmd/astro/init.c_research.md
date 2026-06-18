# File Research: sources/os/plan9/9front/sys/src/cmd/astro/init.c

Initializes object tables and per-time astronomical state.

Important behavior:
- `objlst` lists Sun, Moon, shadow, planets, Pluto, and comet.
- `init` computes observer geocentric latitude/Earth radius corrections and assigns object names/functions.
- `setime` updates ephemeris time, longitude correction, nutation, Sun position, Earth/Sun vector, and Earth velocity approximation.
- `setobj` snapshots current globals into an `Obj1`.
- `fsun`, `fstar`, and `shad` provide special object computations.

This file wires together all object modules for sampling by `main.c`.
