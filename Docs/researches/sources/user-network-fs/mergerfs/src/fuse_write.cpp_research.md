# sources/user-network-fs/mergerfs/src/fuse_write.cpp

## Purpose

`fuse_write.cpp` implements the mergerfs FUSE `write` callback. It writes to FileInfo fds and can migrate files to another branch on ENOSPC/EDQUOT.

## Important APIs, Types, and Functions

functions: `FUSE::write`, `FUSE::write_null`, `ioprio::SetFrom`

## Control Flow

resolve FileInfo, write with pwrite or pwriten depending on direct_io, retry under exclusive per-file mutex on space errors, move file with moveonenospc policy, dup2 the replacement fd, and finish the write

## State and Persistence Behavior

The file has 217 source lines and 5709 bytes. Its direct include set is: `fuse_write.hpp`, `config.hpp`, `errno.hpp`, `fileinfo.hpp`, `fs_close.hpp`, `fs_dup2.hpp`, `fs_movefile_and_open.hpp`, `fs_pwrite.hpp`, `fs_pwriten.hpp`, `ioprio.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: FileInfo fd/branch/fusepath/mutex, cfg.moveonenospc, thread-local ioprio. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
