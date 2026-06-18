# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/conv.c

Contains big-endian disk-format conversion routines for Venti server structures: arena partitions, arena headers and tails, clumps, clump-info records, index sections, index entries, index buckets, and Bloom headers.

The file enforces magic numbers, supported versions, structural sizes, and clump encoding invariants. It handles arena version 4 and 5 formats, including the version-5 clump magic and the arena tail extension that distinguishes committed `diskstats` from in-memory `memstats`.

`packarena()` deliberately clears stale extension fields when no extension is needed, protecting older arenas from a historical sealed-state mismatch. `unpackibucket()` can invalidate buckets when section-specific bucket magic mismatches.

This file is the central compatibility boundary between in-memory `dat.h` structs and stable on-disk bytes.
