# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_backup_super.c

## Purpose
Implements enabling and disabling backup superblock support.

## Main Behavior
- `empty_backup_supers()` clears known backup superblock locations.
- `fill_backup_supers()` writes backup superblocks to known offsets.
- `disable_backup_super()`:
  - No-ops if `OCFS2_FEATURE_COMPAT_BACKUP_SB` is absent.
  - Prompts, clears backup superblock locations, clears compat bit, writes superblock.
- `check_backup_offsets()`:
  - Gets backup super offsets.
  - Loads the global bitmap.
  - Verifies backup locations are not already allocated.
  - Refuses enable when the volume is too small or locations are in use.
- `enable_backup_super()`:
  - No-ops if already enabled.
  - Prompts, checks offsets, writes backup supers, sets compat bit, writes superblock.
- Defines `backup_super_feature` as compat feature with `TUNEFS_FLAG_RW | TUNEFS_FLAG_ALLOCATION`.

## Dependencies
- OCFS2 backup superblock APIs.
- Global bitmap system inode and chain allocator loading.
- Tunefs progress and signal-blocking helpers.

## Notes
Enable does real allocation-safety checking before writing backup blocks. Disable frees/clears backup locations before clearing the feature flag.
