# File Research: sources/local-fs/btrfs-progs/cmds/rescue.c

## Purpose

Defines the `btrfs rescue` command group and command-line frontends for specific offline repair/rescue operations.

## Commands

- `chunk-recover`: validates unmounted device, parses `-y/-v`, calls `btrfs_recover_chunk_tree()`.
- `super-recover`: validates unmounted device, parses `-y/-v`, calls `btrfs_recover_superblocks()`.
- `zero-log`: opens partial writable ctree and clears superblock log root fields.
- `fix-device-size`: opens partial writable ctree and calls `btrfs_fix_device_and_super_size()`.
- `fix-data-checksum`: parses readonly/interactive/mirror modes and calls `btrfs_recover_fix_data_checksum()`.
- `create-control-device`: creates `/dev/btrfs-control` with major/minor `10:234`.
- `clear-uuid-tree`: deletes the UUID tree so the kernel can rebuild it.
- `clear-ino-cache`: removes deprecated inode-cache items.
- `clear-space-cache`: removes v1 or v2 free-space cache.

## Control Flow

Each destructive filesystem operation checks mount status before opening, generally refuses mounted filesystems, and opens the ctree with write flags appropriate to the operation. Several commands also reject running replace/balance through `has_running_replace_or_balance()`.

## Dependencies

Connects command framework macros, help text, open-utils, clear-cache helpers, transaction APIs, and exported rescue backends from `cmds/rescue.h`.

## Risks And Edge Cases

- Return value normalization varies: some functions return `!!ret`, while `super-recover` preserves its documented status codes.
- `clear_uuid_tree()` manually detaches and frees a root after deleting its items and root item; transaction abort/commit handling is explicit but complex.
- `zero-log`, cache clearing, UUID tree clearing, and chunk/super recovery are offline destructive repair operations; correctness relies on mount checks and user confirmation in lower-level backends where applicable.
