# sources/user-network-fs/mergerfs/src/fuse_readlink.cpp

## Purpose

`fuse_readlink.cpp` implements the mergerfs FUSE `readlink` callback. It resolves symlink targets from the selected branch and can expose symlinkify paths for eligible regular files.

## Important APIs, Types, and Functions

types/namespaces: `stat`; functions: `FUSE::readlink`

## Control Flow

search branches for the path, optionally lstat and synthesize a target path when symlinkify applies, otherwise call fs::readlink

## State and Persistence Behavior

The file has 124 source lines and 3399 bytes. Its direct include set is: `fuse_readlink.hpp`, `config.hpp`, `errno.hpp`, `fs_lstat.hpp`, `fs_path.hpp`, `fs_readlink.hpp`, `symlinkify.hpp`, `fuse.h`, `algorithm`, `cstring`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: cfg.readlink policy, symlinkify toggle/timeout, no persistent state. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
