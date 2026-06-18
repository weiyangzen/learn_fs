# File Research: sources/local-fs/xfsdump/common/util.h

## Role

This header declares general utility APIs for manager-buffer I/O, string copying, XFS inode iteration, directory iteration, and pointer alignment.

## Buffer API

Declares callback typedefs and helpers:

- `write_buf()`
- `read_buf()`

These bridge manager zero-copy-ish buffer interfaces with simple caller-owned buffers.

## XFS Iteration API

Defines selector flags:

- `BIGSTAT_ITER_DIR`
- `BIGSTAT_ITER_NONDIR`
- `BIGSTAT_ITER_ALL`

Declares callback types and functions:

- `bigstat_iter()`
- `bigstat_one()`
- `inogrp_iter()`
- `diriter()`

These are central helpers for walking XFS filesystem metadata by inode and directory entry.

## Miscellaneous

- `strncpyterm()` guarantees null termination.
- `COPY_LABEL()` copies fixed global label buffers.
- `ALIGN_PTR()` aligns a pointer upward to an alignment boundary.
