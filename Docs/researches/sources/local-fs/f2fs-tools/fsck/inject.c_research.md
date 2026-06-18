# File Research: sources/local-fs/f2fs-tools/fsck/inject.c

Purpose: implements `inject.f2fs`, a metadata fault-injection utility for F2FS images. It parses injection-specific CLI options and mutates selected on-disk structures: superblocks, checkpoint packs, NAT/SIT entries, summary blocks, node blocks, inode fields, and directory entries.

Key behavior:
- Defines `enum entry_pos` to distinguish metadata entries in current journals versus NAT/SIT pack 1 or pack 2.
- Provides debug printers for raw NAT, SIT, summary, node footer, and dentry structures.
- `inject_parse_options()` handles `--mb`, `--idx`, `--val`, `--str`, `--sb`, `--cp`, `--nat`, `--sit`, `--ssa`, `--node`, `--dent`, `--dots`, `--nid`, `--blk`, `--dry-run`, `-d`, `-V`, and help routing.
- `inject_sb()` reads one superblock copy, changes supported fields (`magic`, `s_stop_reason`, `s_errors`, `feature`, `devs.path`), then calls `update_superblock()`.
- `inject_cp()` can mutate the current or explicitly selected checkpoint pack. It supports core checkpoint fields, curseg arrays, allocation type, checksum, elapsed time, and fsync dnode `next_blkaddr`; it rewrites first and last checkpoint blocks via `write_raw_cp_blocks()`.
- NAT/SIT injection prefers journal entries when present; otherwise it calculates the selected current or alternate pack address and rewrites the corresponding block.
- `inject_ssa()` mutates summary footer fields or per-block summary entries and writes the segment summary block back.
- `inject_node()` mutates node footer fields, inode fields, or direct-node `addr[]`, then writes via `update_inode()` unless explicitly injecting `i_inode_checksum`.
- `inject_dentry()` locates a child entry in inline or regular directory data blocks, supports dot/dotdot selection, and changes bitmap, hash, inode, file type, or filename; filename updates recompute name length and hash.
- `do_inject()` dispatches the selected injection mode and, for host-managed zoned devices, wraps node/dentry injection with fsck initialization plus curseg/journal/SIT/checkpoint flushes.

Important dependencies:
- Uses `node.h` traversal helpers, `get_node_info()`, `get_sum_block()`, `lookup_nat_in_journal()`, `lookup_sit_in_journal()`, `write_sum_block()`, `update_inode()`, `update_block()`, `write_checkpoint()`, and many F2FS endian/accessor macros.
- Relies on global configuration `c`, including `c.private` carrying `struct inject_option`.

Risk notes:
- This file intentionally corrupts or mutates metadata. Bounds checks exist for many array indexes and block/nid ranges, but most I/O uses `ASSERT`, so malformed images can abort the tool.
- `inject_sb()` frees `opt->str`; other string-based injection paths do not, because the option struct is global/static for the process.
- NAT/SIT pack selection uses current version bitmaps when pack is `0`; explicit pack selection can deliberately target stale copies.
