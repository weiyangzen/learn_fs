# File Research: sources/teaching/minix/minix/servers/vfs/write.c

## Purpose
Provides the VFS write syscall entry point as a thin wrapper around shared read/write logic.

## Main Entry Point
- `do_write()` handles `write(fd, buffer, nbytes)`.

## Control Flow
The function rejects requests with nonzero `cum_io`, then delegates to `do_read_write_peek(WRITING, fd, buf, len)` using fields from `job_m_in.m_lc_vfs_readwrite`.

## Dependencies
Includes `fs.h`, `file.h`, and MINIX call numbers. The actual I/O behavior lives in shared read/write code outside this file.

## Risks and Notes
The `cum_io` guard mirrors `do_read()` behavior and prevents unsupported cumulative I/O state from entering the shared write path.
