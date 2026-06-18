# sources/user-network-fs/mergerfs/src/fuse_readdir_base.hpp

## Purpose

This header declares the `FUSE::readdir_base` callback surface. It exists so `mergerfs.cpp` can wire the operation into `fuse_operations` while the implementation stays in the paired source file.

## Important APIs, Types, and Functions

types/namespaces: `FUSE`, `ReadDirBase`

## Control Flow

The declared API participates in the operation that declares a FUSE callback. The header itself only includes the libfuse/base types needed by callers.

## State and Persistence Behavior

The file has 39 source lines and 1157 bytes. Its direct include set is: `fuse.h`, `string_view`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Keep the signature aligned with libfuse and the paired implementation. Behavioral risks and tests are driven by the implementation: no owned state in the header.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
