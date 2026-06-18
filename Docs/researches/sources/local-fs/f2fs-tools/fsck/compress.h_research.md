# File Research: sources/local-fs/f2fs-tools/fsck/compress.h

## Purpose
Public declarations for fsck/sload compression support.

## Key contents
- Includes `f2fs_fs.h`.
- Declares:
  - `supported_comp_names[]`
  - `supported_comp_ops[]`
  - `ext_filter`

## Dependencies
The declared types `compress_ops` and `filter_ops` come from the shared F2FS userspace headers.

## Research notes
This is a narrow interface header. Implementation details and optional library handling are confined to `compress.c`.
