# sources/user-network-fs/mergerfs/src/policy_eplfs.hpp

## Purpose

This header declares the `eplfs` policy implementation classes for action, create, and search categories.

## Important APIs, Types, and Functions

types/namespaces: `Action`, `Create`, `EPLFS`, `Policy`, `Search`

## Control Flow

Each class derives from the corresponding `Policy::*Impl`, gives the policy its configured name, and forwards runtime behavior to the paired `.cpp` file. The policy existing-path least-free-space: among existing copies, choose the branch with the smallest available space that still passes create/action constraints.

## State and Persistence Behavior

The file has 67 source lines and 1819 bytes. Its direct include set is: `policy.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The important contract is whether `Create::path_preserving` returns true; rename and create behavior depend on that distinction.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
