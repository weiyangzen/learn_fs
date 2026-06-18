# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/cubrt.c

Read fully: 30 lines, 329 bytes. SHA-256 prefix: `9bdbddf175662834`.

Provides real cube root `cubrt()`. It handles sign, scales the magnitude into a stable range by factors of 8, then applies Newton iteration until convergence.

Integration: used by `ccubrt()` and projection math.

Risk notes: convergence threshold is absolute (`10.e-15`) and loop has no explicit iteration cap.
