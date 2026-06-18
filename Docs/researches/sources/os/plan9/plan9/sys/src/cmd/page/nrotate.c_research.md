# File Research: sources/os/plan9/plan9/sys/src/cmd/page/nrotate.c

Contains an older or incomplete experimental implementation of logarithmic 180-degree image rotation using draw masks and shuffling.

The visible code sketches mask halving, adjacent-region swaps, slop movement, and range swaps along X/Y axes, but contains unresolved identifiers and incomplete statements, including references such as `swapadjacent`, `moveup`, `lastnn`, `nn`, `n`, `mask`, and `im` in scopes where they are not defined.

Compared with `rotate.c`, this file appears stale and not suitable as the active build source. Its value is mostly historical: it documents the intended divide-and-shuffle rotation algorithm later realized in a compilable form elsewhere.
