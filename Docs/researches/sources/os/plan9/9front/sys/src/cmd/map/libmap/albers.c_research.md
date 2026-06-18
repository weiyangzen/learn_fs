# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/albers.c

Implements spherical and spheroidal Albers equal-area conic projection plus inverse/scaling helpers.

Key pieces:
- `albinit()` normalizes standard parallels, handles degenerate cases by falling back to azimuthal equal-area or cylindrical equal-area, computes constants, and returns `Xspalbers`.
- `albers()` calls `albinit()` with eccentricity zero.
- `sp_albers()` calls it with spheroid eccentricity `EC2`.
- `Xspalbers()` projects using precomputed constants and south-pole orientation.
- `albscale()` and `invalb()` support inverse Albers coordinate scaling and latitude/longitude recovery.

The implementation follows Deetz and Adams formulas and shares static state across the active projection.
