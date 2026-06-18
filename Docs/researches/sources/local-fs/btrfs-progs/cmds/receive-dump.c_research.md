# File Research: sources/local-fs/btrfs-progs/cmds/receive-dump.c

## Purpose

Defines print-only send-stream callbacks used by `btrfs receive --dump`. It decodes send-stream operations into one textual line per operation without applying changes to the filesystem.

## Core Data Flow

The file exports `btrfs_print_send_ops`, a `struct btrfs_send_ops` callback table. Each callback formats one send-stream command.

## Key Helpers

- `PATH_CAT_OR_RET` validates and joins paths.
- `__print_dump()` centralizes output formatting:
  - operation title
  - escaped path
  - optional operation-specific fields
  - special path handling for subvolume/snapshot commands
- `PRINT_DUMP_SUBVOL`, `PRINT_DUMP`, and `PRINT_DUMP_NO_NEWLINE` wrap the print modes.
- `sprintf_timespec()` formats timestamps using local time and `%FT%T%z`.

## Operations Printed

Includes callbacks for:

- subvolume and snapshot creation
- file, directory, fifo, socket, node, and symlink creation
- rename, link, unlink, rmdir
- write and clone operations
- xattr set/remove
- truncate, chmod, chown, utimes
- update_extent
- encoded_write
- fallocate
- fileattr
- enable_verity

## Important Behavior

- Paths and arbitrary xattr data are printed using escaping helpers.
- Clone and rename output expands destination/source paths relative to current subvolume context.
- `enable_verity` prints metadata lengths and algorithm/block size, not the raw salt/signature.
- This file does not parse stream bytes itself; parsing is handled by `common/send-stream` and dispatched through callbacks.
