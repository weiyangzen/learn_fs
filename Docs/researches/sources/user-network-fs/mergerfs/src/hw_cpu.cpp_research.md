# sources/user-network-fs/mergerfs/src/hw_cpu.cpp

## Purpose

`hw::cpu::logical_core_count` exposes the online processor count for configuration defaults.

## Important APIs, Types, and Functions

types/namespaces: `cpu`, `hw`

## Control Flow

It calls `sysconf(_SC_NPROCESSORS_ONLN)` when available and otherwise returns 1.

## State and Persistence Behavior

The file has 36 source lines and 1024 bytes. Its direct include set is: `unistd.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are small but callers should handle zero or negative sysconf returns; tests can stub platform macros or verify positive fallback behavior.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
