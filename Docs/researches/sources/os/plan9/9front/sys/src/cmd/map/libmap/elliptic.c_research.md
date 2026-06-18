# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/elliptic.c

Implements an elliptic projection based on distances to two foci separated by a center longitude/latitude parameter. It falls back to azimuthal equidistant for very small parameter values and rejects parameters over 89 degrees.

`Xelliptic()` computes two angular distances, derives x from squared-distance difference, and derives signed y from the remaining ellipse equation.
