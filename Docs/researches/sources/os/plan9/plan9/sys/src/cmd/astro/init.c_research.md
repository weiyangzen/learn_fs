# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/init.c

Initializes object registry, observer Earth parameters, and time-dependent solar/nutation state.

Key points:
- `objlst` orders all supported bodies: Sun, Moon, shadow, planets, Pluto, and comet.
- `init` computes geocentric latitude and Earth radius factor from observer location and elevation.
- `setime` sets ephemeris date, longitude correction, nutation, Sun vectors, and Earth velocity approximation.
- `setobj` copies current global observable coordinates into an object sample point.
- `fsun` and `shad` compute Sun and Earth shadow pseudo-object positions.

Dependencies:
- Uses global object structs and planetary routines.

Notable behavior:
- `init` is called before and after argument parsing because arguments can change location.
