# sources/user-network-fs/mergerfs/src/hashset.hpp

## Purpose

`HashSet` is a small non-copyable 64-bit hash set used by readdir merging to deduplicate entry names without storing full strings.

## Important APIs, Types, and Functions

types/namespaces: `HashSet`

## Control Flow

`put` hashes names with rapidhash, keeps up to eight hashes inline, grows to a power-of-two open-addressed table, and returns whether the name was newly inserted.

## State and Persistence Behavior

The file has 182 source lines and 3582 bytes. Its direct include set is: `base_types.h`, `rapidhash/rapidhash.h`, `cstring`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

It stores hashes only, so correctness relies on low 64-bit collision probability; tests should cover duplicate names, inline-to-table growth, load-factor growth, and zero-hash remapping.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
