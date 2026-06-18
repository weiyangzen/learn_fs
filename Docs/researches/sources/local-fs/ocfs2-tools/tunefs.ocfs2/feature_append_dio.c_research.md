# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_append_dio.c

## Purpose
Implements `tunefs.ocfs2` enable/disable support for the append direct I/O incompat feature.

## Main Behavior
- `enable_append_dio()`:
  - No-ops if `ocfs2_supports_append_dio()` is already true.
  - Prompts via `tools_interact()`.
  - Sets `OCFS2_FEATURE_INCOMPAT_APPEND_DIO`.
  - Writes the superblock with signals blocked.
- `disable_append_dio()`:
  - No-ops if feature is absent.
  - Prompts.
  - Clears the incompat bit and writes the superblock.
- Defines `append_dio_feature` with `TUNEFS_FLAG_RW | TUNEFS_FLAG_ONLINE`.

## Dependencies
- `ocfs2/ocfs2.h` feature helpers.
- `libocfs2ne.h` tunefs framework, progress, signal-block wrappers, and feature macros.

## Notes
This feature is a pure superblock flag toggle; it performs no inode or allocator migration.
