# File Research: sources/local-fs/reiserfsprogs/reiserfscore/journal.c

## Purpose
`journal.c` opens, validates, creates, replays, prints, and closes ReiserFS journals. It handles both standard journals on the filesystem device and non-standard/separate journals.

## Main Responsibilities
- Validates descriptor and commit block pairs.
- Finds oldest/newest valid transactions in the circular journal area.
- Iterates transactions and transaction blocks.
- Replays journal blocks to their in-place filesystem targets.
- Creates journal headers and initializes superblock journal parameters.
- Opens/reopens/closes journal devices and manages `fs_jh_bh`.
- Checks consistency between superblock journal parameters and journal header parameters.
- Advises valid journal transaction sizing.

## Key Functions
- `does_desc_match_commit()` compares descriptor and commit transaction ID/length.
- `commit_expected()` and `next_desc_expected()` calculate circular journal positions.
- `transaction_check_content()` validates descriptor, commit, and target block journalability.
- `transaction_check_desc()` performs descriptor/commit structural validation.
- `get_boundary_transactions()` scans the journal for valid transactions and records oldest/newest by transaction ID.
- `next_transaction()` advances to the next valid transaction up to a boundary transaction.
- `for_each_block()` maps each journal payload block to its in-place target block and calls an action callback.
- `replay_one_transaction()` writes all transaction blocks to their target locations.
- `for_each_transaction()` iterates valid transactions in order.
- `reiserfs_open_journal()` opens the journal device/file and reads the journal header.
- `reiserfs_create_journal()` validates location/size and writes journal parameters into both journal header and superblock.
- `reiserfs_replay_journal()` replays valid post-header transactions and updates the journal header after each replay.

## Data and Control Flow
Journal replay starts with `reiserfs_replay_journal()`, which reads control state from the journal header, scans for boundary transactions, skips transactions already flushed according to header state, then replays contiguous transactions with matching mount ID and incrementing transaction ID. Each replay copies blocks from the journal device to the filesystem device and writes them synchronously.

Transaction block target numbers are split across descriptor and commit blocks: the first half is in descriptor `j2_realblock`, and the remainder is in commit `j3_realblock`.

## Integration Points
- Uses block classification from `node_formats.c`, especially `who_is_this()` and `not_journalable()`.
- Uses buffer I/O primitives from the local `io` layer.
- Uses progress reporting through `progbar.h`.
- Writes superblock fields and marks filesystem dirtiness during journal creation and replay.

## Risks and Edge Cases
- `next_transaction()` loops until it finds a valid descriptor; a badly damaged circular journal could cause long scans.
- Replay refuses non-journalable targets, protecting superblock-before-area and journal blocks.
- Separate journal creation intentionally caps defaults and warns about oversized journals that can make filesystems hard to mount.
- `reiserfs_journal_params_check()` may repair old standard-journal header mismatch by copying superblock parameters into the journal header.
- Several error paths return numeric status codes with different meanings (`-1`, `0`, `1`, `2`), so callers must preserve semantics.

## Testing Signals
Tests should cover standard and separate journal open/create, too-small journals, journal beyond device size, descriptor/commit mismatch, invalid target blocks, no transactions, already-flushed transactions, contiguous replay, broken transaction stop, and parameter mismatch repair.
