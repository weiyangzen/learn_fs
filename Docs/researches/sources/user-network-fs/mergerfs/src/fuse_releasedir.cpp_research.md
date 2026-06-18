# sources/user-network-fs/mergerfs/src/fuse_releasedir.cpp

## Purpose

`fuse_releasedir.cpp` implements the mergerfs FUSE `releasedir` callback. It releases DirInfo allocated by opendir.

## Important APIs, Types, and Functions

functions: `FUSE::releasedir`

## Control Flow

recover DirInfo from ffi->fh, reject invalid handles, delete it, and return success

## State and Persistence Behavior

The file has 46 source lines and 1179 bytes. Its direct include set is: `fuse_releasedir.hpp`, `config.hpp`, `dirinfo.hpp`, `fuse.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: DirInfo heap ownership. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
