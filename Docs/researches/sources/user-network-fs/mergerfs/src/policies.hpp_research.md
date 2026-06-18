# sources/user-network-fs/mergerfs/src/policies.hpp

## Purpose

This header centralizes policy class includes and declares the `Policies::{Action,Create,Search}` registries.

## Important APIs, Types, and Functions

types/namespaces: `Action`, `Create`, `Policies`, `Search`

## Control Flow

It exposes singleton instances and `find` functions for policy names configured by users.

## State and Persistence Behavior

The file has 125 source lines and 4320 bytes. Its direct include set is: `policy_all.hpp`, `policy_epall.hpp`, `policy_epff.hpp`, `policy_eplfs.hpp`, `policy_eplus.hpp`, `policy_epmfs.hpp`, `policy_eppfrd.hpp`, `policy_eprand.hpp`, `policy_erofs.hpp`, `policy_ff.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Integration is broad: option parsing stores selected policy implementations in `cfg.func.*`.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
