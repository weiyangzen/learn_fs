# File Research: sources/os/linux/linux-stable/fs/jbd2/recovery.c

## Scope
Implements journal mount-time recovery and skip-recovery logic. It scans, validates, revokes, and replays committed log transactions, including descriptor, commit, revoke, checksum, and fast-commit replay handling.

## Primary APIs
Main entry points are `jbd2_journal_recover()` and `jbd2_journal_skip_recovery()`. Internal helpers include `do_one_pass()`, `jread()`, `do_readahead()`, `count_tags()`, checksum verifiers, `jbd2_do_replay()`, `scan_revoke_records()`, and `fc_do_one_pass()`.

## Behavior
Recovery is three-pass:
- `PASS_SCAN` finds the valid transaction range, validates commit records, counts revoke records, tracks head block, and detects stale or corrupt journal tails.
- `PASS_REVOKE` builds the revoke table from revoke blocks.
- `PASS_REPLAY` replays descriptor-tagged data blocks that are not revoked.

`jread()` maps logical journal offsets through `jbd2_journal_bmap()`, reads the physical block, and triggers sequential readahead. Log traversal wraps between `j_first` and `j_last`.

Descriptor replay reads each tagged journal data block, checks block-tag checksums, skips revoked blocks, restores escaped magic numbers, copies data into the filesystem block device buffer, and marks it dirty/uptodate.

Checksum handling supports old transaction checksums plus v2/v3 descriptor, commit, and block-tag checksums. Scan logic distinguishes interrupted commits from stale lazy-init journal contents using commit-time monotonicity and async-commit rules.

Fast commit replay is delegated to `j_fc_replay_callback()` across the fast-commit block range on scan/replay passes, excluding revoke pass.

## State And Data
`struct recovery_info` carries start/end transactions, replay head block, replay count, revoke count, and revoke-hit count. Recovery updates `j_transaction_sequence`, `j_head`, `j_failed_commit`, and temporary replay revoke-table selection.

## Dependencies
Uses revoke APIs from `revoke.c`, log mapping and tag sizing from `journal.c`, block-device sync/flush, checksum helpers, buffer-head I/O, and optional filesystem fast-commit replay callbacks.

## Risks And Invariants
Only complete committed transactions should replay. Revokes for a block at transaction N suppress replay for N and earlier, but not later updates. IO errors attempt partial replay but report failure. Fast-commit replay errors must fall back or fail consistently through the filesystem callback.
