# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/cubrt.c

Provides `cubrt()`, a real cube-root routine. It handles sign, scales the argument into a near-one range by powers of eight, then uses Newton iteration until convergence.

Used by `ccubrt()` and projection formulas needing cube roots.
