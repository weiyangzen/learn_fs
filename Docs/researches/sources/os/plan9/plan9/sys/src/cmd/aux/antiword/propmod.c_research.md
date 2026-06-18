# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/propmod.c

This file stores and retrieves Word property modifier blobs.

Key behavior:
- Maintains a growable array of copied property modifier records.
- `vAdd2PropModList()` stores records whose first word is the byte length.
- `aucReadPropModListItem()` interprets even property modifiers as inline two-byte data and odd modifiers as array indices.
- `vDestroyPropModList()` releases every stored blob and resets counters.

Important details:
- `IGNORE_PROPMOD` returns no modifier.
- Debug builds grow the array in smaller increments than release builds.

Filesystem relevance:
- Indirect: supports fast-save/text-block property metadata recovered from Word file structures.
