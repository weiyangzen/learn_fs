# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/newyorker.c

Implements a “newyorker” radial projection parameterized by angular cutoff `a0`. It computes colatitude `r`, maps the center specially, rejects points inside the cutoff, then uses `log(r/a)` as radial distance.

`newyorker()` stores `a0` in radians and returns `Xnewyorker()`.
