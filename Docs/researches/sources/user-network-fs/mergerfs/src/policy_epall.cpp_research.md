# sources/user-network-fs/mergerfs/src/policy_epall.cpp

## Purpose

`policy_epall.cpp` implements the `epall` branch-selection policy. It existing-path all: action/create/search only include branches where the path already exists; create additionally enforces writable, non-NC, min-free-space checks.

## Important APIs, Types, and Functions

The file implements `Policy::EPAll::Action::operator()`, `Create::operator()`, and `Search::operator()` as applicable through the `Policy` abstraction.

## Control Flow

Control flow scans the configured `Branches`, checks path existence for existing-path variants, filters read-only/no-create branches for mutations, consults `fs::info` or statvfs cache for space metrics, and appends selected `Branch*` entries to the caller-owned output vector.

## State and Persistence Behavior

The file has 142 source lines and 3603 bytes. Its direct include set is: `policy_epall.hpp`, `errno.hpp`, `fs_exists.hpp`, `fs_info.hpp`, `fs_path.hpp`, `fs_statvfs_cache.hpp`, `policy.hpp`, `policy_epall.hpp`, `policy_error.hpp`, `strvec.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are stale space/cache data, unexpected branch ordering effects, and returning a less helpful errno when every branch fails. Test signals should cover missing paths, read-only branches, no-create branches, min-free-space failures, and tie behavior.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
