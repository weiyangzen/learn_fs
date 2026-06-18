# sources/user-network-fs/mergerfs/src/fuse_symlink.cpp

## Purpose

`fuse_symlink.cpp` implements the mergerfs FUSE `symlink` callback. It creates symlinks on selected create branches after cloning required parent paths from an existing branch.

## Important APIs, Types, and Functions

types/namespaces: `stat`; functions: `FUSE::symlink`

## Control Flow

find an existing parent branch, choose create branches, clone directory structure, create symlinks as the caller uid/gid, calculate synthetic inode data, and set cache timeouts based on follow_symlinks

## State and Persistence Behavior

The file has 195 source lines and 5258 bytes. Its direct include set is: `fuse_symlink.hpp`, `config.hpp`, `errno.hpp`, `error.hpp`, `fs_clonepath.hpp`, `fs_lstat.hpp`, `fs_path.hpp`, `fs_inode.hpp`, `fs_symlink_as.hpp`, `fuse_getattr.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: branch directory trees, returned stat/timeouts, cfg symlink/getattr policies. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
