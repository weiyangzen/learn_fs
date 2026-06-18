# File Research: sources/os/linux/linux/fs/ubifs/replay.c

## Role

Implements UBIFS journal replay during mount. It scans log LEBs for bud references, scans/recover/authenticates buds, builds sorted replay entries, applies them to the TNC, fixes lprops for replayed buds, and seeds budgeting state.

## Key APIs

- `ubifs_replay_journal()`
- `ubifs_validate_entry()`

## Important Behavior

Replay first marks the index head LEB as taken and validates that the master-recorded index-head offset matches lprops free space.

`replay_log_leb()` scans the log from `lhead_lnum`, requires the first node to be a commit-start node for the current commit, records `cs_sqnum`, initializes and updates the log hash, validates reference nodes, and adds buds to the replay list. It stops when it reaches an empty/out-of-date log LEB.

`add_replay_bud()` creates a `ubifs_bud`, snapshots the current log hash state into the bud, inserts the bud into UBIFS bud tracking, and records the bud in replay order.

`replay_bud()` scans each bud. If recovery is needed and the bud is the last in its journal head, it uses `ubifs_recover_leb()` so power-cut tail corruption can be repaired. It authenticates nodes when authentication is enabled, accepts unauthenticated trailing nodes only on the last bud, builds replay entries for inode/data/dentry/xentry/truncation nodes, and calculates bud dirty/free space.

Replay entries are sorted by sequence number before application. Directory and xattr entries use name-aware TNC operations. Deletions remove keys, truncation replay removes affected data-node ranges, and inode deletion removes all inode keys unless a later replay entry relinks the inode, which handles `O_TMPFILE` relink cases.

When recovery is active, applied replay entries feed `ubifs_recover_size_accum()` so inode sizes can later be reconciled.

`set_bud_lprops()` updates lprops after replay. It accounts for buds that started at offset zero after garbage collection without an intervening commit, marks bud LEBs taken, and seeks journal-head write buffers to the replayed endpoint.

Finally, `ubifs_replay_journal()` initializes `bi.uncommitted_idx` from dirty znode count and clears replay lists/bud lists before returning.

## Dependencies

Uses log scanning/recovery, authentication hash/HMAC helpers, bud management, TNC add/remove APIs, lprops dirty lookup/change, write-buffer seek, recovery size accumulation, list sorting, and key/name helpers.

## Research Notes

Replay ordering is sequence-number based because journal heads race with each other. Authentication permits missing trailing auth coverage only on the last bud, matching the power-cut model. Lprops correction after replay is essential because bud data may include dirty padding, deletions, truncations, and overwritten nodes.
