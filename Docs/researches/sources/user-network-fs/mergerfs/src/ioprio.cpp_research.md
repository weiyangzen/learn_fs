# sources/user-network-fs/mergerfs/src/ioprio.cpp

## Purpose

This file mirrors a client process I/O priority onto mergerfs worker threads on Linux.

## Important APIs, Types, and Functions

types/namespaces: `ioprio`; functions: `ioprio::SetFrom::_slow_apply`, `ioprio::SetFrom::thread_prio`, `ioprio::enable`, `ioprio::get`, `ioprio::set`

## Control Flow

`get` and `set` wrap `SYS_ioprio_get/set`; `enable` flips an atomic flag; `SetFrom::_slow_apply` reads the client pid priority and updates the current thread only when it changed.

## State and Persistence Behavior

The file has 92 source lines and 1975 bytes. Its direct include set is: `ioprio.hpp`, `errno.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State is `_enabled` plus thread-local `SetFrom::thread_prio`; risks are Linux-only syscall availability and permission failures.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
