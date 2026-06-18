# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/checkarenas.c

Implements `checkarenas`, a normal arena-partition checker and optional fixer. It opens one arena partition, initializes its `ArenaPart`, and checks either all arenas or selected names.

`checkarena()` optionally rescans from the beginning (`-a`) by clearing in-memory stats, then repeatedly calls `syncarena()` until no header update is reported. It compares recomputed `memstats` with the old values and reports incorrect arena header fields.

With `-f`, it copies corrected `memstats` into `diskstats`, writes the arena trailer with `wbarena()`, and flushes the disk cache. Without `-f`, it sets global `readonly`. Verbose modes print arena and partition summaries and final stats.
