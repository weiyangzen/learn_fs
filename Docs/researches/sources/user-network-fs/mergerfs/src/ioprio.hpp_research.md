# sources/user-network-fs/mergerfs/src/ioprio.hpp

## Purpose

This header declares the ioprio API and RAII-like `SetFrom` helper.

## Important APIs, Types, and Functions

types/namespaces: `SetFrom`, `ioprio`; functions: `ioprio::enabled`

## Control Flow

`SetFrom(pid)` cheaply checks the atomic enable flag and applies priority through `_slow_apply` only when enabled.

## State and Persistence Behavior

The file has 61 source lines and 1546 bytes. Its direct include set is: `atomic`, `sys/types.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Integration points are read/write paths; tests should cover disabled no-op behavior and syscall error propagation.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
