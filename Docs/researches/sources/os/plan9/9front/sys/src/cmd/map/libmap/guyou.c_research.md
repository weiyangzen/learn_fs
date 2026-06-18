# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/guyou.c

Implements Guyou projection and a related square projection. Both use stereographic projection, complex transforms, and `elco2()` to map hemispheres/spherical regions to square-like domains.

Key functions:
- `guyou()` initializes elliptic constants, side length, west/east hemisphere centers, and returns `Xguyou()`.
- `Xguyou()` chooses hemisphere, normalizes coordinates, stereographically projects, maps through `dosquare()`, and offsets one hemisphere.
- `guycut()` customizes longitude cuts for Guyou.
- `square()` initializes Guyou constants and returns `Xsquare()`.
- `Xsquare()` maps north/south halves with a fourth-root-like transform and square mapping.

This file depends on complex helpers, `elco2()`, `norm()`, `Xstereographic()`, and cut helpers.
