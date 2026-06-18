# sources/user-network-fs/mergerfs/src/fuse_truncate.cpp

## Purpose

`fuse_truncate.cpp` implements the mergerfs FUSE `truncate` callback. It truncates all policy-selected branch copies.

## Important APIs, Types, and Functions

functions: `FUSE::truncate`

## Control Flow

apply fs::truncate to each selected branch and reconcile partial failures against the getattr policy branch

## State and Persistence Behavior

The file has 109 source lines and 2798 bytes. Its direct include set is: `fuse_truncate.hpp`, `config.hpp`, `errno.hpp`, `fs_path.hpp`, `fs_truncate.hpp`, `policy_rv.hpp`, `fuse.h`, `sys/types.h`, `unistd.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: PolicyRV aggregation and branch file sizes. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
