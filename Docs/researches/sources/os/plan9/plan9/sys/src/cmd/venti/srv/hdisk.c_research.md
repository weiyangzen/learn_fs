# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/hdisk.c

Implements HTTP disk and debug inspection handlers. `/disk` lists configured arena partitions, index sections, and Bloom filter, or opens a selected disk as an arena partition, index section, or Bloom filter.

For arena partitions, it reads the partition table, prints the arena table as links, unpacks selected arena head and tail metadata, displays stats and seal score, lists clump directory entries, and can inspect a clump by offset or score. Clump inspection retries with the raw clump magic when the expected magic fails, decompresses compressed clumps, and recomputes scores.

`hdebug()` supports `op=amap`, `op=mem`, and `op=read`. The read debug path compares cache lookup, disk index lookup, score lookup across all types, arena mapping, and `loadclump()` verification, with optional brute-force arena directory search.

Index-section and Bloom disk pages are stubs in this file.
