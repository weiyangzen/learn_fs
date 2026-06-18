# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/guyou.c

Read fully: 101 lines, 1754 bytes. SHA-256 prefix: `5393501fa448fbd7`.

Implements Guyou and square projections using stereographic mapping plus elliptic integral transformation. `guyou()` initializes constants, hemisphere centers, twist, and side length, then returns `Xguyou`. `Xguyou()` chooses east/west hemisphere, normalizes, stereographically projects, calls `dosquare()`, and offsets x. `square()` initializes Guyou state and returns `Xsquare`, which maps hemispheres to square layout with special antipodal handling.

`guycut()` delegates to map cut helpers and imposes a cut at longitude zero with extra checks near lower latitudes.

Dependencies: `cdiv`, `elco2`, `norm`, `Xstereographic`, `picut`, `ckcut`.

Risk notes: relies on real cut helpers, not `cuts.c` stubs. Static state is shared between Guyou and square.
