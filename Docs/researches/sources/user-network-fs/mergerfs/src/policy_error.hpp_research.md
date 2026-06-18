# sources/user-network-fs/mergerfs/src/policy_error.hpp

## Purpose

This header defines shared policy error-priority logic.

## Important APIs, Types, and Functions

types/namespaces: `policy`

## Control Flow

`error_and_continue` updates the current error and continues; `calc_error` lets ENOENT be replaced by more specific ENOSPC/EROFS and lets later higher-priority errors win.

## State and Persistence Behavior

The file has 51 source lines and 1417 bytes. Its direct include set is: none. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Policy tests should verify returned errors when all branches fail for mixed missing, no-space, and read-only causes.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
