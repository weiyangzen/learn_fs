# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/trapezoidal.c

Implements trapezoidal projection with two standard parallels. It falls back to rectangular when absolute parallels are nearly equal, computes slope `k` and equator offset `yeq`, then maps y linearly by latitude and x as `y*k*longitude`.

`trapezoidal()` returns `Xtrapezoidal()`.
