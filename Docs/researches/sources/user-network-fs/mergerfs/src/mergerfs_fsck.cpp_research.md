# sources/user-network-fs/mergerfs/src/mergerfs_fsck.cpp

## Purpose

This command diagnoses and optionally repairs divergent branch copies visible through a mergerfs mount.

## Important APIs, Types, and Functions

types/namespaces: `FS`, `PathStat`, `stat`; functions: `mergerfs::fsck::main`

## Control Flow

It walks the mergerfs tree, obtains `allpaths` for each entry, compares mode/uid/gid/type/mtime and optional size, then can copy file content or apply owner/mode from a manually selected/newest/largest source.

## State and Persistence Behavior

The file has 467 source lines and 10697 bytes. Its direct include set is: `mergerfs_fsck.hpp`, `fs_close.hpp`, `fs_copyfile.hpp`, `fs_is_same_file.hpp`, `fs_lchmod.hpp`, `fs_lchown.hpp`, `fs_lgetxattr.hpp`, `fs_lstat.hpp`, `fs_open.hpp`, `mergerfs_api.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are destructive repairs, root permission requirements, xattr dependency, and type mismatches requiring manual intervention.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
