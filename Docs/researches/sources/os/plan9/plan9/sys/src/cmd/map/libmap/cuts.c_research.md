# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/cuts.c

Read fully: 39 lines, 844 bytes. SHA-256 prefix: `7ffc05e2f067826c`.

This file provides stub definitions for `picut()`, `ckcut()`, and `reduce()` so `libmap` can stand alone. Comments explain that real implementations live in `map.c`, but unusual projections (`hex.c`, `guyou.c`, `tetra.c`) need these names.

Each stub calls `abort()` and returns a dummy value.

Risk notes: if these stubs are linked instead of the real map program versions, projections using cut logic will abort at runtime.
