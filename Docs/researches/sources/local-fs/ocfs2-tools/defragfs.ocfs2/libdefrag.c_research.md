# File Research: sources/local-fs/ocfs2-tools/defragfs.ocfs2/libdefrag.c

## Role

`libdefrag.c` implements small utility functions for `defragfs.ocfs2`.

## Functions

`do_malloc()` wraps zeroed allocation and exits on failure. `do_read()` and `do_write()` loop until the requested byte count is completed, retrying `EAGAIN` and `EINTR` and returning a negative errno on hard errors.

`do_csum()` computes an Internet-checksum-like 16-bit folded checksum over an arbitrary byte buffer, handling odd alignment and endianness.

## Usage

The record subsystem uses these helpers for allocation, robust record-file I/O, and resume-record checksum validation.

## Risk Areas

Pointer arithmetic is performed on `void *` in the I/O helpers, which is a GNU C extension rather than strict ISO C.
