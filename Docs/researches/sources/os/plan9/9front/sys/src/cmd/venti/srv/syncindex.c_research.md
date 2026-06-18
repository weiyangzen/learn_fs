# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/syncindex.c

`syncindex` is the command-line driver for synchronizing an index from arena contents. It loads config and bloom filter, initializes disk/lump/index caches, starts bloom maintenance, optionally prints the index, calls `syncindex(mainindex)`, then flushes index and disk caches.

It exposes cache-size flags for block and index caches plus verbose mode. This file is orchestration; the actual arena scanning and index insertion live in `syncindex0.c` and `syncarena.c`.
