# File Research: sources/local-fs/btrfs-progs/cmds/receive-dump.h

## Purpose

Declares the dump-mode receive context and callback table used by `receive.c`.

## Main Definitions

- `struct btrfs_dump_send_args`
  - `full_subvol_path[PATH_MAX]`
  - `root_path[PATH_MAX]`

These fields track path context while formatting stream operations.

## Exported Symbol

- `extern struct btrfs_send_ops btrfs_print_send_ops;`

## Role in the Codebase

Provides the bridge between `receive.c` command parsing and the print-only implementation in `receive-dump.c`.
