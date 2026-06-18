# sources/user-network-fs/mergerfs/src/oom.cpp

## Purpose

This file adjusts the current process OOM killer score through `/proc/self/oom_score_adj`.

## Important APIs, Types, and Functions

functions: `oom::get_oom_score_adj`, `oom::has_oom_score_adj`, `oom::set_oom_score_adj`

## Control Flow

It checks for procfs support, reads the current score, and writes a formatted score value.

## State and Persistence Behavior

The file has 68 source lines and 1428 bytes. Its direct include set is: `oom.hpp`, `fs_exists.hpp`, `fmt/core.h`, `fstream`, `tuple`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Risks are permission failures and errno after iostream errors; tests should use an injectable path or filesystem sandbox.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
