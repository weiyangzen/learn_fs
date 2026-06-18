# File Research: sources/local-fs/ocfs2-tools/fswreck/corrupt.c

This file is the central dispatcher from `enum fsck_type` values to specific corruption helper functions.

Key behavior:
- `create_named_directory()` ensures a named directory exists under the root, creating and linking it if absent.
- `corrupt_file()` maps file-oriented corruption codes to helpers for extents, inodes, symlinks, root/special files, directories, inline data, duplicate clusters, and refcount inode fields. It creates/uses a root-level `tmp` directory as the parent object.
- `corrupt_sys_file()` maps system-file corruption codes to chain, superblock, inode orphan/allocation, journal, and quota helpers.
- `corrupt_group_desc()` maps allocation group descriptor corruption codes to group helpers.
- `corrupt_local_alloc()` maps local allocation corruption codes.
- `corrupt_truncate_log()` maps truncate log corruption codes.
- `corrupt_refcount()` maps refcount tree/block corruption codes and uses `tmp` as a parent directory.
- `corrupt_discontig_bg()` directly forwards to discontiguous block-group corruption.

Integration notes:
- The switch coverage must stay synchronized with `fsck_type.h` and `main.c` prompt table.
- Invalid codes terminate via `FSWRK_FATAL`.
- This file has little mutation logic itself; its main risk is stale or incomplete dispatch mapping when new fsck prompt codes are added.
