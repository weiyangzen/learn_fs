# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/arc.c

Manages `Arc` objects in the `mk` dependency graph.

Key functions:
- `newarc()` allocates and initializes an arc from a prerequisite node and rule, copying stem and regexp matches.
- `dumpa()` prints debug information for an arc and nested node.
- `nrep()` reads variable `NREP` to set allowed rule-repetition count, defaulting to at least `1`.

Dependencies:
- `Malloc`, `rcopy`, `symlook`, and debug output through `bout`.
- Arc fields are defined in `mk.h`.
