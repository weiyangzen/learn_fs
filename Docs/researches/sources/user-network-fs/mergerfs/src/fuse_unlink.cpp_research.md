# sources/user-network-fs/mergerfs/src/fuse_unlink.cpp

## Purpose

`fuse_unlink.cpp` implements the mergerfs FUSE `unlink` callback. It unlinks all policy-selected branch copies.

## Important APIs, Types, and Functions

functions: `FUSE::unlink`

## Control Flow

collect unlink action branches, call fs::unlink on each branch path, and return the folded Err result

## State and Persistence Behavior

The file has 77 source lines and 1854 bytes. Its direct include set is: `fuse_unlink.hpp`, `config.hpp`, `errno.hpp`, `error.hpp`, `fs_path.hpp`, `fs_unlink.hpp`, `fuse.h`, `vector`, `unistd.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: branch filesystem entries only. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
