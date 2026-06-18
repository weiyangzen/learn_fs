# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/orthographic.c

Implements orthographic projection and its limb generator. `Xorthographic()` maps visible hemisphere coordinates to x/y and returns hidden status for southern/back-side latitudes. `orthographic()` returns it.

`olimb()` iterates the equatorial limb from longitude -180 to 180 using a static first-call flag.
