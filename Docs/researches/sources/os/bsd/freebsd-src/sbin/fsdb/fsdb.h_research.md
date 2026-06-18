# File Research: sources/os/bsd/freebsd-src/sbin/fsdb/fsdb.h

## Purpose

Shared declarations for `fsdb`.

## Contents

- External fsck utility functions used by fsdb: `blread()`, `rwerror()`, `reply()`.
- Shared device/filesystem state: `dev_bsize`, `secsize`, `fsmodified`, `fsfd`.
- Command metadata structure `struct cmdtable`.
- Command flag definitions for read/write safety.
- Current inode globals: `curip`, `curinode`, `curinum`.
- Utility function prototypes for argument parsing, active inode printing, and active inode validation.

## Integration Notes

Defines the contract between `fsdb.c` and `fsdbutil.c`, while relying on UFS dinode types from the fsck/FFS headers.
