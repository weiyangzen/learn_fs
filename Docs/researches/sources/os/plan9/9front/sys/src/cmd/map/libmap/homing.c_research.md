# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/homing.c

Implements homing and Mecca projections based on azimuth/distance to a chosen standard latitude point.

Key functions:
- `azimuth()` computes bearing (`az`) and angular distance (`rad`) from an input place to `p0`, including pole handling and trigonometric clamping.
- `mecca()`/`Xmecca()` map longitude and bearing-derived y with clipping/visibility rules.
- `homing()`/`Xhoming()` map angular distance along the bearing vector.
- `hlimb()` and `mlimb()` generate limb outlines for homing/Mecca projections.

Static state stores the standard parallel and first-call state for limb generation.
