# sources/user-network-fs/mergerfs/src/num.hpp

## Purpose

This header declares `num::humanize(cu64)`.

## Important APIs, Types, and Functions

types/namespaces: `num`

## Control Flow

It is used by option/config reporting paths that need compact byte-unit strings.

## State and Persistence Behavior

The file has 29 source lines and 917 bytes. Its direct include set is: `base_types.h`, `string`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The API is stateless and returns a `std::string`.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
