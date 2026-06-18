# File Research: sources/os/plan9/9front/sys/src/cmd/ktrans/hash.h

This header declares the `Hmap` structure and hash-map API used by `ktrans`. `Hmap` records bucket count, node size, logical length, capacity, and a byte pointer to node storage.

It also defines `Hkey`, a small union for pointer/int key-like values, though the implementation uses string keys. The public API covers allocation, get, replace, update, delete, key retrieval, and reset.
