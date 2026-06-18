# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/propmod.c

Stores and retrieves Word property modifier byte sequences.

Key routines:
- `vDestroyPropModList()` frees all stored modifier records and resets static list state.
- `vAdd2PropModList()` appends a length-prefixed property modifier buffer, growing the backing array in batches.
- `aucReadPropModListItem()` resolves a `usPropMod` value either as an inline two-byte modifier or as an index into the stored list.

Important behavior:
- `IGNORE_PROPMOD` returns `NULL`.
- Even `usPropMod` values encode modifier data directly.
- Odd `usPropMod` values are treated as list indexes shifted right by one.

Dependencies:
- Shared little-endian helpers and fail-fast allocation wrappers.

Research relevance:
- Supports fast-saved or compressed text runs where paragraph property modifiers are referenced indirectly.
