# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_dirhash.c

Read completely: 1064 lines.

Implements the optional hash-based lookup and free-space index for large UFS directories.

Core behavior:
- `ufsdirhash_build()` decides whether a directory should be hashed, enforces global memory limits, allocates hash/free-space structures, scans directory entries with `UFS_BUFATOFF()`, inserts live entries, and accounts free record space.
- `ufsdirhash_lookup()` looks up a name by SipHash slot, supports sequential-access optimization, validates offsets and directory records, returns the containing buffer and optional previous-entry offset, and falls back to linear lookup on corrupt or recycled state.
- `ufsdirhash_findfree()` uses free-space summaries to locate a block/range suitable for a new entry; `ufsdirhash_enduseful()` identifies trailing empty directory blocks.
- Mutation helpers `ufsdirhash_add()`, `remove()`, `move()`, `newblk()`, and `dirtrunc()` keep hash slots and free-space statistics in sync with directory changes.
- `ufsdirhash_checkblock()` optionally verifies hash state against an on-disk directory block.
- Recycling uses a score-based global list: `ufsdirhash_recycle()` detaches and frees backing arrays from low-score dirhashes while leaving stubs for later rebuild.
- Initialization sets pool state, locks, random SipHash key, default max memory, and minimum directory size.

Integration and risks:
- Locking order is global `ufsdirhash_mtx` before per-dirhash `dh_mtx`.
- Callers must tolerate `dh_hash == NULL` after recycling.
- Incorrect free-space accounting can corrupt create/compact paths.
- Directory corruption causes fallback where possible, but some internal mismatches panic.
