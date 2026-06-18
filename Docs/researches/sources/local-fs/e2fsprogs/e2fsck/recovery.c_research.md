# File Research: sources/local-fs/e2fsprogs/e2fsck/recovery.c

This file is JBD2 journal recovery code adapted for e2fsprogs userland and kernel builds. It scans, revokes, and replays journal transactions after an unclean shutdown.

Core recovery model:
- `jbd2_journal_recover(journal)` performs three passes: `PASS_SCAN`, `PASS_REVOKE`, and `PASS_REPLAY`.
- `jbd2_journal_skip_recovery(journal)` scans only enough to advance transaction state while discarding pending journal contents.
- `struct recovery_info` records start/end transaction IDs and replay/revoke statistics.

Journal reading:
- `jread()` maps a journal offset to a device block, reads it through buffer heads, does readahead where available, and validates bounds.
- Kernel builds include `do_readahead()` to issue sequential journal reads in chunks.
- `wrap()` wraps log offsets across the journal ring, respecting fast-commit bounds when enabled.

Checksums and tags:
- `jbd2_descriptor_block_csum_verify()` verifies descriptor/revoke block tail checksums.
- `jbd2_commit_block_csum_verify()` verifies commit block checksums.
- `jbd2_block_tag_csum_verify()` verifies individual replayed data block checksums.
- `count_tags()` and `read_tag_block()` parse descriptor tags, including 64-bit block numbers and UUID elision.
- `calc_chksums()` computes transaction checksums for older checksum formats during scan.

Main pass engine:
- `do_one_pass()` walks transactions in sequence, reading descriptor, commit, and revoke blocks.
- `PASS_SCAN` finds the valid end of the log and handles checksum failures, async commit, stale lazy-init journal blocks, and commit-time ordering.
- `PASS_REVOKE` scans revoke records into the revoke table.
- `PASS_REPLAY` copies unrecalled journaled blocks back to the filesystem device, honoring revoke records and escaped magic values.
- Fast commits are delegated to `fc_do_one_pass()` through `j_fc_replay_callback`.

Revoke scanning:
- `scan_revoke_records()` validates record count, chooses 32-bit or 64-bit block record size, and calls `jbd2_journal_set_revoke()` for each revoked block.

Integration points:
- Uses revoke helpers from `revoke.c`.
- Uses JBD2 journal superblock fields, feature flags, buffer-head IO, and checksum helpers.
- After recovery, clears revoke state, syncs the block device, and flushes if barriers are enabled.

Risk notes:
- Recovery can continue after some replay IO errors but reports failure at the end.
- Checksum mismatch handling distinguishes likely stale journal blocks from corruption using commit-time monotonicity.
- Replayed buffers are marked dirty and released; final persistence depends on later sync/flush.
