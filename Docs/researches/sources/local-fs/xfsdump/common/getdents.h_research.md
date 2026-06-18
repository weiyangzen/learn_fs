# File Research: sources/local-fs/xfsdump/common/getdents.h

## Summary
Declares `getdents_wrap()`, the local wrapper for reading directory entries through Linux `getdents64`.

## Interface
`int getdents_wrap(int fd, char *buf, size_t nbytes);`

The caller supplies a directory fd, output buffer, and byte capacity. Return semantics follow getdents-style conventions: positive byte count, zero at end, or `-1` with `errno`.

## Risks
The header exposes only a raw byte-buffer API, so callers must know the expected record layout and iterate entries correctly.
