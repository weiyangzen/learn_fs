# sources/sync-backup/casync/src/cachunker.c

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cachunker.c -->
## sources/sync-backup/casync/src/cachunker.c

Purpose: `cachunker.c` implements casync's content-defined chunk boundary scanner using a rolling buzhash. It supports configurable min/average/max sizes and a fixed-size special case.

Important APIs and functions: `ca_chunker_set_size` validates and computes chunk sizing parameters and the discriminator. `ca_chunker_start` initializes rolling hash state over a full window. `ca_chunker_roll` advances the hash by removing one byte and adding another. `ca_chunker_scan` consumes data until it finds a boundary or reports that more data is needed.

Control flow: size configuration fills zero values from defaults or proportional values, bounds them by `CA_CHUNK_SIZE_LIMIT_MIN/MAX`, and computes a discriminator adjusted by `CA_CHUNKER_DISCRIMINATOR_FROM_AVG`. Scanning skips boundary checks until the minimum size window can matter, fills the 48-byte window, then rolls over incoming bytes. A boundary occurs at max size or when `hash % discriminator == discriminator - 1`. On boundary, hash/window/chunk counters reset.

State and persistence: all state is in the caller-owned `CaChunker`: rolling hash, window bytes, window size, current chunk size, configured sizes, and discriminator. No persistent I/O is performed.

Dependencies and integration points: depends on `cachunk.h` for hard chunk size limits and `util.h` for rotation/min/assert/log helpers. Higher-level chunkers feed file data through `ca_chunker_scan` to split streams before hashing and storing chunks.

Risks: `ca_chunker_set_size` returns `-EBUSY` once scanning has started (`window_size != 0`), so callers must configure early. The average-size discriminator is approximate and assumes common min/max ratios. Fixed-size mode has separate control flow and should be tested. Passing empty buffers is not explicitly accepted because `ca_chunker_scan` asserts `p`.

Test signals: `test-cachunker` and histogram tests should validate default distribution, configured min/max bounds, fixed-size cuts, streaming behavior across calls, and low-level buzhash start/roll consistency.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cachunker.c -->
