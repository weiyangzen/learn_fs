# sources/user-network-fs/mergerfs/src/fuse_setxattr.cpp

## Purpose

`fuse_setxattr.cpp` implements the mergerfs FUSE `setxattr` callback. It sets extended attributes on branch copies and implements mergerfs control xattr commands/settings.

## Important APIs, Types, and Functions

functions: `FUSE::setxattr`

## Control Flow

handle .mergerfs control keys and command xattrs, block security.capability when disabled, honor global xattr mode, apply lsetxattr across action branches, then map partial failures through getxattr policy

## State and Persistence Behavior

The file has 230 source lines and 6105 bytes. Its direct include set is: `fuse_setxattr.hpp`, `config.hpp`, `errno.hpp`, `fs_glob.hpp`, `fs_lsetxattr.hpp`, `fs_path.hpp`, `fs_statvfs_cache.hpp`, `num.hpp`, `policy_rv.hpp`, `str.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: cfg mutable options, statvfs cache timeout, PolicyRV, and control xattr command side effects. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
