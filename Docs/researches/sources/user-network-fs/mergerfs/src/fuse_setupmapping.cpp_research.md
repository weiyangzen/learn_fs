# sources/user-network-fs/mergerfs/src/fuse_setupmapping.cpp

## Purpose

`fuse_setupmapping.cpp` implements the mergerfs FUSE `setupmapping` callback. It advertises unsupported FUSE setupmapping.

## Important APIs, Types, and Functions

functions: `FUSE::setupmapping`

## Control Flow

return -ENOSYS

## State and Persistence Behavior

The file has 34 source lines and 1207 bytes. Its direct include set is: `fuse_setupmapping.hpp`, `sys/types.h`, `errno.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: no persistent state. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
