# File Research: sources/os/linux/linux/fs/fs_dirent.c

## Purpose
This file provides small exported helpers for converting between Linux generic file-mode bits, filesystem on-disk file type values (`FT_*`), and userspace directory entry type values (`DT_*`). It centralizes mappings that many filesystem drivers need when filling directory entries or storing lightweight inode type metadata.

## Main Definitions
- `fs_dtype_by_ftype[FT_MAX]` maps on-disk `FT_*` constants to `DT_*` constants.
- `fs_ftype_by_dtype[DT_MAX]` maps `DT_*` directory entry type values back to `FT_*`; uninitialized entries default to `FT_UNKNOWN`.
- `fs_ftype_to_dtype(unsigned int filetype)` returns `DT_UNKNOWN` when the supplied filetype is out of range.
- `fs_umode_to_ftype(umode_t mode)` converts `S_DT(mode)` into an on-disk `FT_*` type.
- `fs_umode_to_dtype(umode_t mode)` composes the previous two helpers.

## Control Flow And Behavior
The implementation is table-driven and intentionally has no allocation or locking. Invalid on-disk file type numbers are clamped to `DT_UNKNOWN`, while invalid/unrecognized mode-derived directory types fall through the zero-initialized `fs_ftype_by_dtype` table as `FT_UNKNOWN`.

## Dependencies And Interfaces
The file depends on `<linux/fs_dirent.h>` for type constants and `S_DT()`, and exports all three helpers with `EXPORT_SYMBOL_GPL`. The consumers are expected to be filesystem implementations that need consistent directory entry type conversions.

## Concurrency And Safety
The tables are static constant data and are safe in any context. The kernel-doc comments explicitly state “Any context” for all helpers.

## Research Notes
This is foundational glue rather than policy code. Its main correctness property is that unsupported or impossible values degrade to unknown type instead of fabricating a specific type.
