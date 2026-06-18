# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/cylequalarea.c

Implements cylindrical equal-area projection. `cylequalarea()` rejects standard parallels above 89 degrees, stores `cos(par)^2` as x scale, and returns `Xcylequalarea()`, which maps longitude linearly and y to `sin(lat)`.
