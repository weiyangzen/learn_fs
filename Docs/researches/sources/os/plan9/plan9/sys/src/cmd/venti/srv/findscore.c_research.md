# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/findscore.c

Implements `findscore`, a read-only utility that searches an arena partition's clump directories for a given score.

`findscore()` walks each arena's `ClumpInfo` records in chunks, compares scores, and reports matching clump number, type, uncompressed size, compressed size, and arena-relative data position. It tracks positions by summing `ClumpSize + ci->size`.

The command parses a score string, opens an arena partition, initializes cache, scans all arenas, and reports total occurrences. `clumpinfoeq()` is a small equality helper for complete `ClumpInfo` comparisons.
