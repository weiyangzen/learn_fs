# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_type.c

## Purpose

Implements `/proc/<pid>/etype`, exposing the target process executable/sysent ABI name.

## Main Entry Point

`procfs_doproctype()` prints `p->p_sysent->sv_name` when available, otherwise `Not Available`, followed by newline.

## Integration Points

Registered by `procfs.c` as read-only `etype`.

## Risks and Review Notes

This is a simple formatter. The output depends on `p_sysent` being present and named for the process ABI.
