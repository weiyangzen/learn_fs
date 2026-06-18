# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idsdata.h

Defines the generic dictionary stack structure.

Key points:
- `dict_stack_t` embeds a `ref_stack_t` of dictionaries.
- Tracks `min_size`, the stack size after clearing.
- Tracks `userdict_index` because Level 1/Level 2 switching substitutes globaldict behavior without changing minimum stack size.
- Caches `def_space` to quickly decide whether `def` can store a value into the top dictionary.
- Caches packed top-dictionary keys, pair count, and values for fast lookup.
- Stores a cached copy of the bottom system dictionary.
- Provides GC descriptor macro as a suffix of `ref_stack_t`.

Research notes:
- The top-entry caches are recomputed after GC, so they are intentionally not declared as GC pointers.
