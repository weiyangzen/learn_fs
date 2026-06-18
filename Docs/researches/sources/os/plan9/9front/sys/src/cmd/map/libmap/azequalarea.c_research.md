# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/azequalarea.c

Implements azimuthal equal-area projection centered on the north pole. `Xazequalarea()` computes radius `sqrt(1 - sin(lat))` and maps by negative longitude sine/cosine. `azequalarea()` returns that function.

This projection is also reused by Aitoff and Albers fallback paths.
