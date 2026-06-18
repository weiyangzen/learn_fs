# sources/user-network-fs/mergerfs/src/fuse_readdir_cor.cpp

## Purpose

`fuse_readdir_cor.cpp` implements the mergerfs FUSE `readdir_cor` callback. It implements concurrent-open/concurrent-read directory merging across all branches.

## Important APIs, Types, and Functions

functions: `FUSE::ReadDirCOR`

## Control Flow

reset the output dirents, enqueue one branch task per branch in a ThreadPool, use a HashSet and mutex to deduplicate names while appending, and fold worker errors through Err

## State and Persistence Behavior

The file has 105 source lines and 2913 bytes. Its direct include set is: `fuse_readdir_cor.hpp`, `supported_getdents64.hpp`, `config.hpp`, `dirinfo.hpp`, `error.hpp`, `fuse_readdir_cor_getdents.icpp`, `fuse_readdir_cor_readdir.icpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: ThreadPool lifetime in ReadDirCOR and per-call HashSet/mutex state. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
