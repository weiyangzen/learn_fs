# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/laue.c

Implements Laue projection. It only accepts points above roughly 45 degrees latitude, computes radius as `tan(PI - 2*lat)`, rejects large radii, and maps by longitude sine/cosine.

`laue()` returns `Xlaue()`.
