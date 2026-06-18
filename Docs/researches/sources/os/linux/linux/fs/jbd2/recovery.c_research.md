# File Research: sources/os/linux/linux/fs/jbd2/recovery.c

## Role

`recovery.c` implements JBD2 on-disk journal recovery. It scans journal records after an unclean shutdown, discovers the valid transaction range, records revoke entries, replays non-revoked metadata blocks to the filesystem device, and resets the journal head/tail state for normal operation.

## Recovery Flow

The main entry point is `jbd2_journal_recover()`.

Recovery uses three passes over the log:
- `PASS_SCAN`: finds the end of valid committed transactions, validates checksums, counts revoke records, tracks the recovery head block.
- `PASS_REVOKE`: builds the revoke table so replay can skip blocks invalidated by later revokes.
- `PASS_REPLAY`: copies non-revoked journaled data blocks back to their home filesystem blocks.

If the journal is already clean (`j_tail == 0`), recovery is skipped and transaction sequence/head fields are initialized from the superblock.

## Core Helpers

- `jread()`: maps a journal offset to a device block, reads the buffer, starts direct journal readahead, validates uptodate status, and returns a `buffer_head`.
- `do_readahead()`: issues sequential readahead over up to 128 KiB of journal blocks.
- `count_tags()`: counts descriptor tags, respecting checksum tails, UUID elision, and last-tag flags.
- `read_tag_block()`: reconstructs 32-bit or 64-bit target block numbers from descriptor tags.
- `calc_chksums()`: computes legacy transaction checksum coverage across descriptor and payload blocks.
- `jbd2_do_replay()`: processes descriptor tags, reads each journal payload block, checks revokes and tag checksums, restores escaped magic values, and dirties the target filesystem buffer.
- `scan_revoke_records()`: counts or installs revoke records from revoke blocks.

## Checksums and Corruption Handling

The file supports:
- Descriptor block checksum verification with `jbd2_descriptor_block_csum_verify()`.
- Commit block checksum verification with `jbd2_commit_block_csum_verify()`.
- Partial commit block checksum verification for incomplete commit blocks.
- Per-data-block tag checksum verification with `jbd2_block_tag_csum_verify()`.

`PASS_SCAN` is careful with checksum failures because stale journal blocks can appear after lazy initialization or wraparound. It uses commit timestamps to distinguish likely stale records from real corruption where possible. Failed valid transactions set `j_failed_commit` or return `-EFSBADCRC`.

## Fast Commit Replay

`fc_do_one_pass()` replays the fast-commit area between `j_fc_first` and `j_fc_last` by calling the filesystem-provided `j_fc_replay_callback()`. It is invoked for scan and replay-style passes when fast commits are enabled, but skipped for revoke pass.

The expected commit id for fast-commit replay is based on the end transaction found by the full journal scan.

## Revoke Semantics

During `PASS_REVOKE`, revoke records are inserted through `jbd2_journal_set_revoke()`. During replay, `jbd2_journal_test_revoke()` suppresses writing any block whose transaction id is older than or equal to the latest revoke for that block. Later journal entries after a revoke can still replay.

## Completion Behavior

After recovery:
- `j_transaction_sequence` is advanced past the last recovered transaction.
- `j_head` is set to the recovery head block.
- The revoke table is cleared and any temporary oversized replay revoke table is destroyed.
- The filesystem device is synced, writeback errors are checked, and an optional flush is issued when barriers are enabled.

## Important Invariants

- Journal log offsets wrap between `j_first` and `j_last`.
- Non-scan passes must end at the same transaction id discovered by `PASS_SCAN`.
- Replay writes to `j_fs_dev`, while journal reads come from `j_dev`.
- Revoke record count from `PASS_SCAN` can trigger a larger temporary revoke hash table for replay.
- Escaped data blocks have the JBD2 magic restored before being dirtied on the filesystem device.

## Research Notes

This file is conservative about recovering as much valid data as possible while reporting I/O or checksum failures. The most subtle logic is in scan-time checksum handling, where stale wrapped journal blocks and interrupted commits must not be misinterpreted as valid transactions.
