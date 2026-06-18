# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/recovery.c

This file implements userland journal-head discovery and clean-journal marking, adapted from GFS2 kernel recovery code.

Public APIs:
- `lgfs2_replay_incr_blk()`
- `lgfs2_replay_read_block()`
- `lgfs2_get_log_header()`
- `lgfs2_find_jhead()`
- `lgfs2_clean_journal()`

Behavior:
- Maps logical journal blocks to physical blocks through `lgfs2_block_map()`.
- Reads log headers, validates block number, legacy hash, and CRC when present.
- Finds a good log header by scanning around invalid segments.
- Binary-searches and scans to find the highest sequence-number journal head.
- Writes a new unmount log header after the head to mark the journal clean.

Integration role:
- Used by fsck/recovery-style tools that need journal state inspection or cleanup.
- Depends on buffer I/O, block mapping, log hash/CRC helpers, and ondisk endian conversion.

Risk notes:
- Comments explicitly say kernel recovery code should be kept in sync.
- Clean-journal writes modify journal metadata directly.
- Zero CRC is accepted for pre-v2 log headers.
- Returns mix negative errno, positive invalid-header code, and zero success; callers must preserve semantics.
