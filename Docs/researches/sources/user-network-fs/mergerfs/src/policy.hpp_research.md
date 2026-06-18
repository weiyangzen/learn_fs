# sources/user-network-fs/mergerfs/src/policy.hpp

## Purpose

This header defines the abstract policy model used by branch-selection code.

## Important APIs, Types, and Functions

types/namespaces: `Action`, `ActionImpl`, `Create`, `CreateImpl`, `Policy`, `Search`, `SearchImpl`

## Control Flow

`ActionImpl`, `CreateImpl`, and `SearchImpl` are virtual implementations; lightweight `Action`, `Create`, and `Search` wrappers hold raw singleton pointers, forward calls, expose names, and for create expose `path_preserving`.

## State and Persistence Behavior

The file has 197 source lines and 3785 bytes. Its direct include set is: `branches.hpp`, `strvec.hpp`, `fs_path.hpp`, `string`, `memory`, `vector`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Null wrappers can be converted to false but most callers assume configured non-null implementations.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
