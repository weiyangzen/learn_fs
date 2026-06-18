# sources/sync-backup/casync/src/cachunker.h

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cachunker.h -->
## sources/sync-backup/casync/src/cachunker.h

Purpose: `cachunker.h` exposes the content-defined chunker state structure, constants, initializer, and scanning functions.

Important APIs and types: `CA_CHUNK_SIZE_AVG_DEFAULT` is 64 KiB. `CA_CHUNKER_WINDOW_SIZE` is 48 bytes. `CA_CHUNKER_DISCRIMINATOR_FROM_AVG(avg)` encodes the empirical average-size correction. `CaChunker` stores hash, window counters, configured min/max/avg sizes, discriminator, and the rolling window. `CA_CHUNKER_INIT` initializes default min/avg/max and discriminator. Public functions configure size, scan data, and expose low-level buzhash start/roll for tests.

Control flow contract: callers initialize with `CA_CHUNKER_INIT`, optionally call `ca_chunker_set_size` before scanning, then feed data to `ca_chunker_scan` until it returns an offset or `(size_t)-1`.

State and persistence: state is entirely in the struct and is reset on discovered chunk boundaries. No heap allocation or persistent storage is implied by the header.

Dependencies and integration points: includes integer, size, and boolean headers. It integrates with `cachunker.c` and higher-level encoding/chunking code.

Risks: because the struct is public, external callers can corrupt invariants if they mutate fields directly. The macro discriminator uses floating-point constants and casts to `size_t`, so extreme averages should be validated through `ca_chunker_set_size`.

Test signals: tests should use both public scan behavior and the exported low-level hash functions. ABI-sensitive consumers should be rebuilt if struct fields change.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cachunker.h -->
