# File Research: sources/local-fs/xfsdump/restore/mmap.h

## Summary
Declares the restore helper `mmap_autogrow()`.

## Interface
`void *mmap_autogrow(size_t len, int fd, off_t offset);`

The caller provides a byte length, backing file descriptor, and mapping offset. Return semantics follow `mmap()`: a valid pointer or `MAP_FAILED`.

## Risks
The header does not include the system types needed for `size_t` and `off_t`; callers must include suitable system headers first.
