# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/part.c

`part.c` abstracts Venti disk partitions and file-backed ranges. It parses `file:lo-hi` names with `K/M/G/T` suffixes, opens the underlying file/device, records offset and bounded size, and falls back from read-write to read-only when needed.

`rwpart()` enforces partition bounds and splits I/O into `Maxxfer` chunks before calling `pread`/`pwrite`. `readpart()` and `writepart()` are thin wrappers. `partblocksize()` records each partition’s block size and updates global `maxblocksize`.

This file is used by almost every Venti storage tool. It provides the range safety layer between arena/index code and raw devices, though `flushpart()` is currently a no-op in this tree.
