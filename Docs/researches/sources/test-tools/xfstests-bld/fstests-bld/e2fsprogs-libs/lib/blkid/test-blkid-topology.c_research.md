# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/test-blkid-topology.c

## Purpose
`test-blkid-topology.c` is a sample/test program for the util-linux blkid v2 compatibility functions implemented in `topology.c`.

## Important APIs, Types, and Functions
The single `main()` uses `blkid_new_probe_from_filename()`, `blkid_probe_get_topology()`, the topology getter family, `blkid_probe_enable_partitions()`, `blkid_do_fullprobe()`, `blkid_probe_lookup_value()`, and `blkid_free_probe()`.

## Control Flow
The program opens a probe for `argv[1]`, prints logical/physical sector and io-size topology, enables partition probing as a compatibility no-op, performs a full probe, and reports whether `TYPE` or `PTTYPE` was found.

## State, Persistence, Dependencies, Risks, and Test Signals
It owns only the probe handle and duplicated lookup strings returned by the library. Dependencies include `<blkid/blkid.h>` and a readable block device or image. Risks are minimal but include missing argument validation and leaked lookup strings. Test signals are successful output on block devices and graceful error exits for failing topology/probe calls.
