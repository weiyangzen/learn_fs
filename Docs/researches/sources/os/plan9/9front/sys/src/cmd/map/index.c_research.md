# File Research: sources/os/plan9/9front/sys/src/cmd/map/index.c

This file registers map projections by name. It defines small adapter functions that normalize constructor signatures to `proj (*)(double,double)`, then fills `struct index index[]`.

Each entry names the projection, constructor, number of parameters, cut function, default flags/parameters, spheroid flag, and optional limb callback. Registered projections include Aitoff, Albers, azimuthal variants, conic/cylindrical variants, Guyou, hex, homing/mecca, Mercator, orthographic/perspective, polyconic, tetra, trapezoidal, Vander Grinten, and others.

This is the projection dispatch table used by the map command/library front end.
