# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/topology.c

## Purpose
`topology.c` emulates a small subset of util-linux blkid v2 APIs needed by e2fsprogs and xfsprogs while delegating actual content detection to this legacy libblkid cache/probe stack.

## Important APIs, Types, and Functions
It defines private `blkid_struct_probe` and `blkid_struct_topology`. Public functions include `blkid_new_probe_from_filename()`, `blkid_free_probe()`, `blkid_do_fullprobe()`, `blkid_probe_enable_partitions()`, `blkid_probe_lookup_value()`, `blkid_probe_get_topology()`, and topology getter functions.

## Control Flow
A probe stores the filename, fd, optional cache, detected device, and last topology values. Full probing creates a cache and calls `blkid_get_dev()`. Value lookup duplicates a tag value from the detected device. Topology fetch issues Linux block ioctls for alignment, minimum/optimal I/O, and sector sizes, defaulting unsupported values to zero.

## State, Persistence, Dependencies, Risks, and Test Signals
State persists for the probe lifetime and includes an open fd and cache reference. Dependencies include Linux `BLKALIGNOFF`, `BLKIOMIN`, `BLKIOOPT`, `BLKSSZGET`, `BLKPBSZGET`, and libblkid internals. Risks include Linux-only ioctls, no real partition scanning despite the enable API, heap-owned values returned through `data`, and stale topology after device changes. Test signals come from `test-blkid-topology.c`.
