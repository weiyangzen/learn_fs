# File Research: sources/virtualization/libblockdev/src/plugins/fs/nilfs.c

Implements NILFS2 support for libblockdev’s filesystem plugin.

Key entry points:
- `bd_fs_nilfs2_is_tech_avail()` checks supported modes and required utilities.
- `bd_fs_nilfs2_mkfs()` runs `mkfs.nilfs2 -q`.
- `bd_fs_nilfs2_set_label()` and `_set_uuid()` use `nilfs-tune`.
- `bd_fs_nilfs2_get_info()` parses `nilfs-tune -l`.
- `bd_fs_nilfs2_resize()` runs `nilfs-resize -y`.
- `bd_fs_nilfs2_check_label()` and `_check_uuid()` validate label/UUID values.

Core mechanics:
- Dependencies are `mkfs.nilfs2`, `nilfs-tune`, and `nilfs-resize`.
- Check and repair modes are explicitly unsupported.
- Mkfs options map label, dry run, no-discard, force, and extra args.
- A `NULL` UUID generates a UUID locally with libuuid, then passes it to `nilfs-tune -U`.
- Info parsing extracts block size, device size, and free block count from colon-prefixed `nilfs-tune` output, while UUID/label come from common probing.
- Resize accepts optional byte size and passes it directly to `nilfs-resize`.

Important invariants:
- NILFS2 labels are capped at 80 characters.
- NILFS2 resize is documented as requiring the filesystem to be mounted; generic code handles temporary mounting.
- No fsck/check/repair operation is provided.

Filesystem/block relevance:
- Provides user-space NILFS2 management through nilfs-utils tools, especially online resize and metadata query.

Notable risks:
- Info parsing depends on exact `nilfs-tune -l` line prefixes.
- Generated UUIDs depend on local libuuid behavior rather than nilfs-utils random generation.
