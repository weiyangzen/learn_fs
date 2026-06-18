# File Research: sources/local-fs/dosfstools/src/file.h

Public interface for fsck path-specific operations.

Contents:
- Defines `FD_TYPE`: `fdt_none`, `fdt_drop`, `fdt_undelete`.
- Defines `FDSC`, a linked tree of fixed 8.3 names and requested operation.
- Declares global `fp_root`.
- Declares short-name formatting/conversion and descriptor-tree functions.

Role:
- Connects CLI `-d`/`-u` path arguments to directory traversal in `check.c`.
