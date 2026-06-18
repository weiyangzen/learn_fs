# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/alloc.c

Implements allocation and addressing for `Memimage`.

Key functions:
- `memimagemove`: updates `Memdata` after compaction-style movement.
- `allocmemimaged`: wraps existing `Memdata` with a `Memimage`.
- `_allocmemimage`: allocates backing memory and metadata.
- `_freememimage`: reference-counted release of backing data.
- `wordaddr`, `byteaddr`: convert image points to backing-memory addresses.
- `memsetchan`: parses channel descriptors into depth, flags, shifts, masks, and channel counts.

Important behavior:
- Computes `zero` so arbitrary rectangle origins, including negative x, map correctly into backing storage.
- Uses `memdefcmap` automatically for color-mapped images.
