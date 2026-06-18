# File Research: sources/os/plan9/9front/sys/src/cmd/astro/mars.c

Computes Mars’s apparent position.

Important behavior:
- Sets Mars orbital elements and solves elliptic orbit.
- Converts to ecliptic coordinates, sets motion and semi-diameter.
- Computes phase-angle based magnitude correction from elongation relative to the Sun.
- Calls common `helio()` and `geo()` transforms.

The module has no perturbation table; perturbation variables are present but zero.
