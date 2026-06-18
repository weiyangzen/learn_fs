# sources/storage-engines/wiredtiger/src/cursor/cur_version.c

## Purpose
Implements debug version cursors that expose all visible or raw historical versions for a key, including in-memory update-chain entries, the on-disk image, and history-store records. Values are returned as metadata columns followed by the underlying value.

## Important APIs, types, and functions
`__wt_curversion_open` initializes `WT_CURSOR_VERSION`, opens a read-only file cursor, optionally opens a history-store cursor, freezes a connection pinned timestamp when the first version cursor opens, parses `debug.dump_version.*` options, and installs methods. `WT_CURVERSION_METADATA_FORMAT` defines ten timestamp/transaction fields plus type, prepare, flags, and location bytes. Main helpers include `__curversion_process_chain`, `__curversion_process_on_disk`, `__curversion_process_hs`, `__curversion_next_single_key`, `__curversion_skip_starting_updates`, `__curversion_value_return_from_upd`, `__curversion_value_return_from_disk_image`, and `__curversion_value_return_from_hs`.

## Control flow
Setting a key resets version state and forwards key packing to the underlying file cursor. Search requires snapshot isolation, verifies the file cursor is not already positioned, performs a key-only btree search, skips aborted/invisible starting updates, and returns the newest version. `next` either advances within one key or, with `cross_key`, walks to the next btree key after all versions for the current key are exhausted. For one key, processing order is update chain, on-disk image, then history store. Tombstones record stop metadata before advancing to value updates. Modify updates are reconstructed before value return. Timestamp-order and start-timestamp modes prune duplicates or stop when older versions are no longer relevant.

## State, persistence, and dependencies
The cursor stores `next_upd`, exhaustion flags for update/on-disk/history-store phases, stop transaction/timestamps/prepared metadata, optional `start_timestamp`, file cursor, and history-store cursor. It does not mutate persistent data, but it reads volatile update chains, stable on-page time windows, and history-store records. Dependencies include btree cursor internals, update visibility, prepared-state atomics, transaction global pinned timestamps, history-store cursor APIs, modify reconstruction, time-window macros, and standard cursor packing.

## Integration points
Version cursors are debug/open-cursor functionality layered over ordinary file cursors. They integrate with transaction visibility and history-store internals, require snapshot isolation for stable global visibility, and expose raw-key/value and cross-key options for diagnostic tooling and Python API marking via `WT_CURSTD_VERSION_CURSOR`.

## Risks and test signals
Risk is high because the cursor interprets MVCC internals. Important cases include prepared rollback visibility, tombstone stop metadata, globally visible pruning, start timestamp cutoff, history-store modify reconstruction, on-disk overflow restart, cross-key reset, raw mode metadata/data splitting, and correct decrement of `version_cursor_count` on close. Tests should cover row and variable-column pages, in-memory btrees, history-store present/absent, prepared updates and tombstones, timestamp-order output, visible-only output, show-prepared-rollback restrictions, snapshot-isolation enforcement, and failure cleanup after partial open.
