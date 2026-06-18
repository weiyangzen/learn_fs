# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/mercator.c

Implements spherical and spheroidal Mercator projections. `Xmercator()` maps x to negative longitude and y to the standard logarithmic Mercator formula, rejecting latitudes beyond about 80 degrees. `Xspmercator()` applies an eccentricity correction using `ECC`.

Constructors are `mercator()` and `sp_mercator()`.
