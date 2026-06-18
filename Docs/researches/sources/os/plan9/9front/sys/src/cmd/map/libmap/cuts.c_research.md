# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/cuts.c

This file supplies aborting placeholder definitions for `picut()`, `ckcut()`, and `reduce()` so the library can be self-standing when unusual projection modules reference cut helpers normally provided by `map.c`.

The comments explain that `hex.c`, `guyou.c`, and `tetra.c` need internal cut knowledge, but these duplicate symbols should not normally be loaded in the full map program.
