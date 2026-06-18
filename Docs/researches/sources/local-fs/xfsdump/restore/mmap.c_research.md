# File Research: sources/local-fs/xfsdump/restore/mmap.c

## Summary
Provides `mmap_autogrow()`, a Linux replacement for IRIX-style `MAP_AUTOGROW` behavior. It extends a backing file before mapping so the requested shared writable mapping is accessible.

## Main Responsibilities
- `fstat()` the target file.
- If the file is smaller than `offset + len`, seek to the last required byte and write one NUL byte.
- Call `mmap()` with `PROT_READ | PROT_WRITE` and `MAP_SHARED`.

## Dependencies
Depends on POSIX `fstat`, `lseek`, `write`, and `mmap`.

## Risks
The `lseek()` and `write()` calls used to extend the file are not checked. If either fails, the subsequent `mmap()` may fail or map a file smaller than expected.

`offset + len` is not overflow-checked.

The function always requests read/write shared mappings; it is not a general-purpose mmap wrapper.
