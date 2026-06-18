# File Research: sources/os/plan9/9front/sys/src/cmd/astro/sun.c

Computes the Sun’s ecliptic position and apparent properties.

Important behavior:
- Computes Earth/Sun orbital elements and perturbation arguments for Moon and planets.
- Uses `sunfp`/`suncp` tables for anomaly, longitude, latitude, and radius corrections.
- Sets solar radius vector, motion, semi-diameter, and magnitude.
- Does not call `helio()`/`geo()` itself; wrappers such as `fsun` handle apparent transforms.

This provides the base Earth/Sun vector used by other object computations.
