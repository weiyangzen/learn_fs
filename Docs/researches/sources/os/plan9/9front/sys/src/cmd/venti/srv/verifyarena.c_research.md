# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/verifyarena.c

`verifyarena` verifies arena seal checksums from stdin or an arena partition. It reads each selected arena, hashes all bytes with the final score slot zeroed, unpacks the trailer, validates name/version consistency, and reports verified, unsealed, or mismatched checksum status.

When run on a partition, it parses the arena-part table and can filter by arena names. Flags control I/O block size, sleep between reads, and verbosity.

The tool does not repair; it is a read-only integrity checker for sealed arena images and partitions.
