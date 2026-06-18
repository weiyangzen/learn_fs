# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/conic.c

Implements a simple conic projection with one standard parallel. For near-zero parallels it falls back to cylindrical projection. `Xconic()` rejects points too far from the standard parallel, computes a radial term, maps longitude scaled by `sin(stdpar)`, and returns hidden/visible status based on radius.

Static state stores the standard parallel.
