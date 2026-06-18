# File Research: sources/os/linux/linux/fs/ntfs3/super.c

## Role

Implements NTFS3 filesystem registration, mount/remount context handling, boot-sector parsing, superblock initialization/teardown, procfs exposure, statfs/show-options/sync/shutdown, NFS export hooks, metadata cache cleanup, discard, and module init/exit.

## Major Areas

- Logging:
  - `ntfs_printk()` and `ntfs_inode_printk()` provide rate-limited filesystem/inode diagnostics.
- Shared upcase table:
  - `ntfs_set_shared()` and `ntfs_put_shared()` deduplicate identical `$UpCase` tables across mounted volumes.
- Mount options:
  - `ntfs_fs_parameters[]` accepts uid/gid/masks, immutable, discard, force, sparse, nohidden, hide-dot-files, Windows names, showmeta, ACL, iocharset, prealloc, nocase, and delalloc.
  - `ntfs_fs_parse_param()` parses and validates parameters.
  - `ntfs_fs_reconfigure()` handles remount, with checks for unreplayed journal, dirty volume, and iocharset consistency.
- Procfs:
  - Creates `/proc/fs/ntfs3/<dev>/volinfo` and `label`.
  - Allows label writes through `ntfs_set_label()` on writable mounts.
- Inode cache and super operations:
  - `ntfs_alloc_inode()`, `ntfs_free_inode()`, `init_once()`.
  - `ntfs_sops` wires allocation, eviction, put_super, statfs, show_options, shutdown, sync, and write_inode.
- Teardown:
  - `ntfs3_put_sbi()` closes bitmaps, drops metadata inodes, updates MFT mirror, clears indexes.
  - `ntfs3_free_sbi()` frees allocated tables, compression contexts, shared upcase, and superblock state.
  - `ntfs_put_super()` clears dirty state when possible and releases options.
- Sync/stat/export:
  - `ntfs_statfs()` reports cluster counts adjusted for delayed allocation.
  - `ntfs_sync_fs()` writes metadata inodes, clears dirty state if successful, updates MFT mirror, and flushes block device.
  - NFS export hooks reconstruct inodes from MFT reference/generation.
- Boot parsing:
  - `ntfs_init_from_boot()` reads primary boot sector, falls back to alternative boot, validates NTFS signature, sector/cluster sizes, MFT locations, MFT/index record sizes, volume size, 32-bit cluster limits, and initializes geometry/maxbytes/MFT-zone/new-record template.
- Mount body:
  - `ntfs_fill_super()` loads `$Volume`, `$MFTMirr`, `$LogFile`, replays log, enforces dirty-volume policy, loads `$MFT`, initializes MFT bitmap and volume bitmap, handles `$BadClus`, reads `$AttrDef`, reads and shares `$UpCase`, initializes `$Secure`, `$Extend`, `$Reparse`, `$ObjId`, then loads root.
  - Updates primary boot from valid alternative boot when appropriate.
- Discard and metadata unmap:
  - `ntfs_unmap_meta()` cleans block-device aliases over metadata ranges.
  - `ntfs_discard()` aligns to device discard granularity and issues trim when enabled.
- Module registration:
  - `ntfs_init_fs_context()`, `ntfs3_kill_sb()`, `ntfs_fs_type`, `init_ntfs_fs()`, `exit_ntfs_fs()`.

## Important Invariants

- RW mount is denied if log replay is required but cannot be completed.
- Dirty volumes require `force` for RW mount.
- Boot-derived cluster size must be at least media sector size.
- MFT and index record sizes must be power-of-two, sector-sized or larger, and no more than 4096 bytes.
- `$Bitmap` must be large enough for all volume clusters.
- `$UpCase` must be exactly 65536 UTF-16 entries.
- The root inode must load and have inode operations before `s_root` is installed.
- `fc->s_fs_info` ownership is transferred through fs context and kill-super paths; option pointers are swapped on reconfigure.

## Dependencies

- Linux fs context, block device, procfs, seq_file, exportfs, NLS, module, statfs, buffer-head APIs.
- NTFS3 internal metadata loaders from inode, fsntfs, index, bitmap, security, objid, reparse, xattr, and logging code.

## Notes For Future Work

- Mount sequencing is critical: `$Volume` before `$LogFile`, `$MFT` before bitmaps, `$UpCase` before case-sensitive operations, and security/extend metadata before normal root use.
- The alternative boot repair path writes block 0 after successful root load; tests around read-only, fake boot sectors, and partial failure would be valuable.
- `ntfs_discard()` caches `-EOPNOTSUPP` by setting `NTFS_FLAGS_NODISCARD`, avoiding repeated unsupported trim attempts.
