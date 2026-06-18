# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/dump.c

Provides text dump helpers for Venti structures.

`printindex()` prints index name, version, block size, table size, bucket divisor, section map, and arena map. `printarenapart()` prints arena partition metadata and arena table entries. `printarena()` prints arena name, address range, version, timestamps, seal state, score if present, clump counts, data sizes, and storage use.

These are shared by command-line diagnostics such as `checkarenas` and `findscore`.
