# File Research: sources/os/linux/linux-stable/fs/hostfs/hostfs_user_exp.c

## Purpose

Exports hostfs syscall-wrapper symbols for GPL modules.

## API Surface

Uses `EXPORT_SYMBOL_GPL()` for all hostfs user adapter functions, including stat/access/open/read/write/metadata/namespace/statfs helpers.

## Dependencies

Includes `<linux/module.h>` and `hostfs.h`.

## Risks

This file makes the hostfs syscall adapter available across object boundaries. The exported function list must stay synchronized with `hostfs.h` and the build split.
