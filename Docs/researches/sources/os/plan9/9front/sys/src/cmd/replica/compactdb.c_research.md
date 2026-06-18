# File Research: sources/os/plan9/9front/sys/src/cmd/replica/compactdb.c

Compacts a replica database by loading it through the AVL-backed database layer and writing one canonical record per live entry to stdout.

This removes append-only tombstones and superseded records while preserving current metadata.
