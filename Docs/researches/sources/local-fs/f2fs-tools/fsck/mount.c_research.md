# File Research: sources/local-fs/f2fs-tools/fsck/mount.c

Purpose: implements the userspace “mount” lifecycle for fsck-family tools: superblock/checkpoint validation, metadata manager construction, NAT/SIT/summary loading and flushing, checkpoint writing, fsync recovery recording, and teardown.

Key behavior:
- Provides debug printers for ACLs, xattrs, inode/node data, extension lists, superblock fields, checkpoint fields, checkpoint state flags, superblock stop reasons, and recorded filesystem errors.
- Zoned-device helpers determine usable segments and zone capacity constraints.
- `f2fs_is_valid_blkaddr()` validates metadata/data block ranges by address type.
- `f2fs_ra_meta_pages()` performs metadata readahead for NAT/SIT/SSA/CP/POR.
- `update_superblock()` recomputes superblock CRC when enabled and writes selected superblock copies.
- `sanity_check_raw_super()` verifies magic, checksums, block/sector geometry, segment/section/zone counts, extension counts, cp payload, reserved inode numbers, zoned feature compatibility, and area boundaries.
- `validate_super_block()` reads a candidate superblock, runs sanity checks, captures kernel/mkfs versions, sets invalid-superblock flags, and reports stop/error state.
- `get_valid_checkpoint()` validates both checkpoint packs, compares checkpoint versions, selects the newest valid pack, copies payload blocks, and marks fsck needed if only one pack is valid.
- `sanity_check_ckpt()` validates and can repair selected checkpoint accounting/layout fields under fix-on policy.
- NAT manager setup loads version bitmap, initializes NID bitmaps early from journal and later from NAT, checks or writes NAT bits.
- Segment manager setup builds SIT info, current segment state, and summary blocks from compacted or normal summaries.
- `build_sit_entries()` reads current SIT blocks plus SIT journal entries into segment entries and counts free segments.
- `build_nat_area_bitmap()` builds fsck NAT bitmaps/cache from NAT packs and NAT journal entries.
- NAT/SIT helpers support journal lookup, flushing journals into packs, nullifying NAT entries, rewriting SIT area bitmaps, updating NAT/data block addresses, and retrieving summaries.
- Curseg allocation helpers find free blocks, move current segments, set section types, relocate curseg offsets, zero journals, and write curseg fields back into checkpoint.
- `write_checkpoint()` recomputes checkpoint counts, flags, checksum, summary blocks, optional NAT bits, and writes first/last checkpoint blocks with fsync ordering.
- `write_checkpoints()` mirrors the valid checkpoint before repairing checkpoint pack 1.
- Fsync recovery support scans warm-node chains, detects loops with Floyd’s algorithm, optionally fixes loops, records fsync inode/data blocks into checkpoint-valid maps, and triggers roll-forward state.
- `f2fs_do_mount()` orchestrates the full mount path: superblock selection, sector tuning, checkpoint loading, fsck/kernel gates, feature tuning, manager builds, fsync record, proceed checks, late manager/NID initialization, and NAT bits validation.
- `f2fs_do_umount()` frees node, segment, SIT, curseg, checkpoint, and superblock memory.
- Android sparse support zeros SIT/NAT/payload metadata regions after sload.

Important dependencies:
- Central dependency for nearly every file in this group: `node.c`, `inject.c`, quota checks, fsck verification, sload/defrag, and summary/NAT/SIT helpers all depend on this mount state.
- Uses global config `c` for mode, fix policy, features, sparse mode, zoned model, kernel checks, and cached geometry.

Risk notes:
- This is the highest-blast-radius file in the group. Many repair writes are guarded by `c.fix_on`, but many reads/writes abort through `ASSERT`.
- Checkpoint and NAT/SIT journal flushing changes persistent metadata and can cascade into checkpoint rewrites.
- Fsync node-chain loop detection returns `-ELOOP` as a nonfatal fsck continuation path unless repair is enabled.
