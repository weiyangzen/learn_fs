# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/azequidist.c

Implements azimuthal equidistant projection. `Xazequidistant()` uses colatitude `PI/2 - lat` as radius and maps by negative longitude sine/cosine. `azequidistant()` returns the projection function.
