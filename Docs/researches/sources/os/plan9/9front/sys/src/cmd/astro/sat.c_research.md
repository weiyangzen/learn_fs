# File Research: sources/os/plan9/9front/sys/src/cmd/astro/sat.c

Computes Saturn’s apparent position and ring-influenced magnitude.

Important behavior:
- Sets Saturn mean orbital elements and solves elliptic orbit.
- Applies fixed longitude/latitude adjustments.
- Computes Saturn ring geometry relative to Earth and Sun to derive magnitude.
- Calls common `helio()` and `geo()` transforms.

This module is the apparent source for copied ring-magnitude blocks in the outer planet files.
