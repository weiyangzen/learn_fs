# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/printarenapart.c

`printarenapart` reads an arena partition header and table, then prints summary information for each listed arena. It manually reads each arena header and tail, decodes disk stats, and reports clumps, compressed clumps, used bytes, uncompressed size, seal state, creation time, and modification time.

The file contains an unused `rdarena()` helper similar to `printarena.c`, but `threadmain()` only emits partition/arena summaries. It uses raw table parsing rather than full `initarenapart()`.

This is a diagnostic view for arena partitions when the operator wants layout and usage metadata instead of all clump entries.
