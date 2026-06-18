# sources/user-network-fs/mergerfs/src/policies.cpp

## Purpose

This file instantiates all policy singleton objects and implements name lookup for action, create, and search categories.

## Important APIs, Types, and Functions

local static helpers and declarations visible through the paired header

## Control Flow

The `IFERT` macro lists every registered policy and `find` returns the matching singleton pointer or null.

## State and Persistence Behavior

The file has 136 source lines and 5481 bytes. Its direct include set is: `policies.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are registry drift when adding a policy and static initialization assumptions.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
