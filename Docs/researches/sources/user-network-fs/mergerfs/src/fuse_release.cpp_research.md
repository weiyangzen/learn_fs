# sources/user-network-fs/mergerfs/src/fuse_release.cpp

## Purpose

`fuse_release.cpp` implements the mergerfs FUSE `release` callback. It closes FileInfo handles and tears down shared open-file state created by fuse_open.

## Important APIs, Types, and Functions

functions: `FUSE::passthrough_close`, `FUSE::release`

## Control Flow

optionally fadvise DONTNEED twice, decrement state.open_files refcount under erase_if, close passthrough backing IDs and canonical/per-handle fds after map mutation

## State and Persistence Behavior

The file has 138 source lines and 4397 bytes. Its direct include set is: `fuse_release.hpp`, `state.hpp`, `config.hpp`, `fileinfo.hpp`, `fs_close.hpp`, `fs_fadvise.hpp`, `fuse_passthrough.hpp`, `fuse.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: state.open_files, FileInfo lifetime, cfg.dropcacheonclose. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
