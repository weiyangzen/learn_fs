# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/polyconic.c

Implements polyconic projection. For non-equatorial latitudes it uses cotangent latitude and longitude scaled by sine latitude. Near the equator it uses series approximations to avoid division by near-zero sine.

`polyconic()` returns `Xpolyconic()`.
