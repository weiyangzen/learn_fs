# sources/user-network-fs/mergerfs/src/mergerfs_api.cpp

## Purpose

This file implements a lightweight API for interrogating mounted mergerfs instances through `.mergerfs` and `user.mergerfs.*` xattrs.

## Important APIs, Types, and Functions

local static helpers and declarations visible through the paired header

## Control Flow

It detects mounts via `.mergerfs`, reads all key/value settings through `fs::xattr::get`, and exposes basepath/relpath/fullpath/allpaths by reading fixed xattr names.

## State and Persistence Behavior

The file has 112 source lines and 2767 bytes. Its direct include set is: `mergerfs_api.hpp`, `fs_xattr.hpp`, `fs_exists.hpp`, `fs_lgetxattr.hpp`, `str.hpp`, `scope_guard/scope_guard.hpp`, `array`, `cstring`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

It depends on xattr availability and a 64 KiB buffer; tests should include missing xattrs, NUL-split allpaths, and non-mergerfs paths.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
