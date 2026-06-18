# sources/test-tools/fio/os/mac/posix.h

## Purpose
`os/mac/posix.h` declares the macOS `posix_fadvise()` compatibility shim and defines the advice constants that fio's common code expects.

## Important APIs, Types, and Functions
It defines `POSIX_FADV_NORMAL`, `POSIX_FADV_RANDOM`, `POSIX_FADV_SEQUENTIAL`, and `POSIX_FADV_DONTNEED`, and declares `int posix_fadvise(int fd, off_t offset, off_t len, int advice)`.

## Control Flow
There is no runtime control flow in the header; the implementation is in `posix.c`.

## State and Persistence
The header has no state. It enables common fio code to request macOS file-cache advice through the compatibility function.

## Dependencies and Integration Points
It is included by `os-mac.h`, which exposes `CONFIG_POSIX_FADVISE` for macOS builds. It relies on the including context to provide `off_t`.

## Risks and Edge Cases
The constants are local compatibility values, not necessarily OS-native ABI values. All callers must link the corresponding `posix.c` implementation.

## Test Signals
Build/link tests for macOS and runtime fadvise tests through fio's `fadvise_hint` option validate this file.
