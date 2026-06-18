# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_osrel.c

## Purpose

Implements `/proc/<pid>/osrel`, exposing and allowing updates to a process’s ABI OS release value.

## Main Entry Point

`procfs_doosrel()`:
- rejects calls without a `uio`.
- on read, emits `p->p_osrel` followed by newline.
- on write, trims and finishes the sbuf, parses only decimal digits, detects integer wrap by checking monotonic accumulation, and stores the parsed value in `p->p_osrel`.

## Integration Points

Registered by `procfs.c` as `osrel` with `PFS_RDWR`, `procfs_attr_rw`, and `procfs_candebug`.

## Risks and Review Notes

The parser accepts only unsigned decimal text after trimming and does not accept whitespace or signs. Write access is gated by procfs debug permission rather than by a file-local privilege check.
