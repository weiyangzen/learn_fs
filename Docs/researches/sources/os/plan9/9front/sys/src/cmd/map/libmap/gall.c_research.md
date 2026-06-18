# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/gall.c

Implements Gall projection. `gall()` rejects standard parallels over 80 degrees, computes a longitude scale from the parameter, and returns `Xgall()`. The projection maps x linearly and y as `tan(lat/2)`, with an alternate formula for numerical stability away from the equator.
