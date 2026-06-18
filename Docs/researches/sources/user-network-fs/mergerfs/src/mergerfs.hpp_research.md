# sources/user-network-fs/mergerfs/src/mergerfs.hpp

## Purpose

This placeholder-style header is the include anchor for the main mergerfs executable translation unit.

## Important APIs, Types, and Functions

local static helpers and declarations visible through the paired header

## Control Flow

It exports no local declarations; integration is by convention through `mergerfs.cpp`.

## State and Persistence Behavior

The file has 19 source lines and 817 bytes. Its direct include set is: none. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The main risk is accidental dependency growth if declarations are later added without separating executable-only concerns.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
