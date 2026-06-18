# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/harrison.c

Implements Harrison perspective-like projection with radius `r` and angle `alpha`. Initialization computes view/unit constants and rejects invalid geometry. `Xharrison()` projects 3D sphere coordinates onto a plane using those constants, rejecting points behind/too near the view plane or outside radius bounds.
