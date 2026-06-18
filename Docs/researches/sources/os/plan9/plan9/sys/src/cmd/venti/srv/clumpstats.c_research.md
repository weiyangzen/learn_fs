# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/clumpstats.c

Implements `clumpstats`, a read-only utility that summarizes stored clumps by uncompressed size and Venti type.

It loads the Venti config, initializes disk cache, then `readarenainfo()` walks every arena's clump directory in chunks of 32K `ClumpInfo` records. Valid entries increment a global `count[size][type]` table; invalid type or size entries are reported and skipped.

`clumpstats()` totals clump records across all arenas and prints one row per non-empty size, followed by per-type counts. It is diagnostic only and does not inspect clump payloads.
