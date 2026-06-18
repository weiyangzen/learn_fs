# File Research: sources/local-fs/f2fs-tools/fsck/resize.c

Implements `resize.f2fs` metadata relocation for growing and safe shrinking F2FS volumes.

Key responsibilities:
- Computes a target superblock layout in `get_new_sb()`: `block_count`, segment counts, SIT/NAT/SSA positions, main-area start, section count, reserved segments, and overprovisioning.
- Handles checkpoint bitmap pressure through `cp_payload`, including large NAT bitmap support and checkpoint checksum offset changes.
- Migrates existing main-area valid blocks in `migrate_main()`, copying data/node blocks to the new offset and updating either data block addresses or NAT entries from summary metadata.
- Rewrites SSA through `move_ssa()` / `migrate_ssa()`, including packed SSA support via 4 KiB sub-block writes.
- Shrinks NAT only if soon-to-be-removed NAT blocks are all zero in `shrink_nats()`, then rewrites NAT set 0 and clears NAT bitmap in `migrate_nat()`.
- Rebuilds SIT from in-memory segment entries in `migrate_sit()`, remapping old segment numbers by the relocation offset.
- Rebuilds checkpoint packs in `rebuild_checkpoint()`: updates counts, current segment numbers, version bitmaps, NAT bits flags, checksum, orphan blocks, summary blocks, and disables the old checkpoint.
- Entry point `f2fs_resize()` dispatches grow vs shrink based on target block count.

Important control flow:
- Grow: flush journals, derive `new_sb`, validate capacity, optionally shrink NAT, defragment if the new main area overlaps old main data, migrate main if needed, migrate SSA/NAT/SIT, rebuild checkpoint, write both superblocks.
- Shrink: requires `c.safe_resize`, flushes journals, validates capacity, checks NAT shrink safety, defragments blocks past the new end into remaining space, writes new superblock, rebuilds checkpoint. Several full metadata migration calls are present but commented out.

Notable dependencies:
- Uses global configuration `c`, superblock helpers from `f2fs_fs.h`, fsck metadata helpers from `fsck.h`, segment summaries, NAT/SIT bitmaps, checkpoint helpers, and defragmentation.
- Uses `update_data_blkaddr()` and `update_nat_blkaddr()` to keep logical mappings consistent after physical relocation.

Behavioral notes:
- Safe shrink is intentionally constrained; non-safe shrink is rejected.
- Expanding with `safe_resize` is rejected.
- Assertions are heavy and usually abort the tool on I/O or metadata invariant failure.
- The user-facing message has a typo: `"reszie wanted"` and `"defragement"`, but behavior is unaffected.
