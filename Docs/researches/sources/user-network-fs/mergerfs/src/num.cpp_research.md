# sources/user-network-fs/mergerfs/src/num.cpp

## Purpose

This file formats byte counts into exact binary unit strings.

## Important APIs, Types, and Functions

types/namespaces: `num`

## Control Flow

`num::humanize` returns raw bytes unless the value is evenly divisible by K, M, G, or T, choosing the largest exact unit.

## State and Persistence Behavior

The file has 54 source lines and 1544 bytes. Its direct include set is: `ef.hpp`, `num.hpp`, `fmt/core.h`, `inttypes.h`, `stdio.h`, `stdlib.h`, `time.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Tests should include boundary values, non-even sizes, zero, and TB-scale values.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
