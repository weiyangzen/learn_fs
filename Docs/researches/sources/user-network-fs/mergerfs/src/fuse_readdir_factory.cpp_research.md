# sources/user-network-fs/mergerfs/src/fuse_readdir_factory.cpp

## Purpose

`fuse_readdir_factory.cpp` implements the mergerfs FUSE `readdir_factory` callback. It parses the readdir mode string and builds seq, cosr, or cor implementations.

## Important APIs, Types, and Functions

functions: `FUSE::ReadDirBase`, `FUSE::ReadDirCOR`, `FUSE::ReadDirCOSR`, `FUSE::ReadDirFactory`, `FUSE::ReadDirSeq`

## Control Flow

match type[:concurrency[:queue-depth]], derive defaults from hardware_concurrency, bound nonpositive values, and return the matching ReadDirBase instance

## State and Persistence Behavior

The file has 121 source lines and 3244 bytes. Its direct include set is: `fuse_readdir_factory.hpp`, `fuse_readdir_cor.hpp`, `fuse_readdir_cosr.hpp`, `fuse_readdir_seq.hpp`, `array`, `cassert`, `cmath`, `cstdio`, `cstdlib`, `regex`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: no global state; constructed objects own any thread pools. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
