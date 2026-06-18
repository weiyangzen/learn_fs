# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/sinusoidal.c

Implements sinusoidal projection. `Xsinusoidal()` maps x to negative longitude times `cos(lat)` and y to latitude. `sinusoidal()` returns it.

This projection is also used as a Bonne fallback.
