# File Research: sources/os/linux/linux-stable/fs/orangefs/downcall.h

## Scope

This header defines kernel-visible OrangeFS downcall response structures returned by the userspace client daemon.

## APIs And Structures

- Defines per-operation responses for I/O, lookup, create, symlink, getattr, mkdir, statfs, mount, xattr, params, perf counters, fs keys, and feature negotiation.
- `struct orangefs_downcall_s` contains type, status, optional trailer metadata, and a union of operation responses.
- `struct orangefs_readdir_response_s` describes the header stored in READDIR trailers.

## Dependencies And Role

- Included through `orangefs-dev-proto.h` together with upcall definitions.
- Layout is shared across kernel/userspace protocol boundaries and uses fixed-width integer types plus explicit padding.

## Risks And Invariants

- Trailer buffers are currently used only for READDIR.
- Fixed buffer sizes such as `PERF_COUNT_BUF_SIZE` and `FS_KEY_BUF_SIZE` define userspace-visible ABI limits.
