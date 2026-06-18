# sources/user-network-fs/mergerfs/src/fuse_readdir_cosr.cpp

## Purpose

`fuse_readdir_cosr.cpp` implements the mergerfs FUSE `readdir_cosr` callback. It implements concurrent-open/sequential-read directory listing.

## Important APIs, Types, and Functions

functions: `FUSE::ReadDirCOSR`

## Control Flow

use the thread pool to open branches, then consume the resulting DirRV futures to append merged entries to the output buffer

## State and Persistence Behavior

The file has 77 source lines and 2055 bytes. Its direct include set is: `fuse_readdir_cosr.hpp`, `config.hpp`, `dirinfo.hpp`, `supported_getdents64.hpp`, `fuse_readdir_cosr_getdents.icpp`, `fuse_readdir_cosr_readdir.icpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: ThreadPool lifetime in ReadDirCOSR and transient future list. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
