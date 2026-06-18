# sources/user-network-fs/mergerfs/src/fuse_rename.cpp

## Purpose

`fuse_rename.cpp` implements the mergerfs FUSE `rename` callback. It renames paths across branch copies while respecting path-preserving create policies and configured EXDEV behavior.

## Important APIs, Types, and Functions

functions: `FUSE::rename`, `FUSE::symlink`

## Control Flow

choose preserve-path or create-path algorithm, rename matching branch copies, clone destination parent paths when needed, remove stale destinations, and on EXDEV optionally stage old paths under .mergerfs_rename_exdev plus symlink

## State and Persistence Behavior

The file has 368 source lines and 9308 bytes. Its direct include set is: `fuse_rename.hpp`, `config.hpp`, `error.hpp`, `errno.hpp`, `fs_clonepath.hpp`, `fs_link.hpp`, `fs_mkdir_as.hpp`, `fs_path.hpp`, `fs_remove.hpp`, `fs_rename.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: branch filesystem contents, cfg.rename_exdev, cfg.ignorepponrename, rename/getattr/create policies. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
