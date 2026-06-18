# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/albers.c

Read fully: 117 lines, 2397 bytes. SHA-256 prefix: `31ad7fe8f49fa5b9`.

Implements spherical and spheroidal Albers equal-area conic projection plus inverse/scale helpers. `albinit()` normalizes standard parallels, handles degenerate cases by returning azimuthal/cylindrical alternatives, computes eccentricity-dependent constants, and returns `Xspalbers`. `sp_albers()` uses `EC2`, while `albers()` uses zero eccentricity.

`albscale()` computes inverse-based twist/scale for a reference point. `invalb()` inverts x/y back to latitude/longitude iteratively.

Dependencies: `deg2rad`, `azequalarea`, `cylequalarea`.

Risk notes: projection constants are static globals, so concurrent different Albers instances would conflict.
