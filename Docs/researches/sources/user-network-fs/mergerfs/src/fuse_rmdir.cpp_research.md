# sources/user-network-fs/mergerfs/src/fuse_rmdir.cpp

## Purpose

`fuse_rmdir.cpp` implements the mergerfs FUSE `rmdir` callback. It removes directories across policy-selected branch copies and can unlink symlink-followed pseudo-directories.

## Important APIs, Types, and Functions

types/namespaces: `RmdirErr`; functions: `FUSE::rmdir`

## Control Flow

collect action branches, call rmdir on each full path, optionally unlink on ENOTDIR when following symlinks, and prioritize ENOTEMPTY/EEXIST in RmdirErr

## State and Persistence Behavior

The file has 149 source lines and 3443 bytes. Its direct include set is: `fuse_rmdir.hpp`, `config.hpp`, `errno.hpp`, `fs_path.hpp`, `fs_rmdir.hpp`, `fs_unlink.hpp`, `fuse.h`, `string`, `unistd.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: RmdirErr aggregation and cfg.follow_symlinks. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
