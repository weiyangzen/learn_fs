# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/ccubrt.c

Provides `ccubrt()`, a complex cube-root helper. It converts the complex input to polar form, cube-roots the radius with `cubrt()`, divides the angle by three, and returns rectangular coordinates.

Used by conformal map projections such as hex.
