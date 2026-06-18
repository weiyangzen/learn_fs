# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/simpleconic.c

Implements a simple conic projection with two standard parallels. It falls back to rectangular when parallels sum to near zero, computes constants differently for equal versus distinct parallels, and maps by radius `r0 - lat` and longitude scale `a`.

`simpleconic()` returns `Xsimpleconic()`.
