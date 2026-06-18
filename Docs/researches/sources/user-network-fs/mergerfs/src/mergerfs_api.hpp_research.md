# sources/user-network-fs/mergerfs/src/mergerfs_api.hpp

## Purpose

This header declares the public `mergerfs::api` helpers for mount detection, config reads, and path mapping.

## Important APIs, Types, and Functions

types/namespaces: `api`, `mergerfs`

## Control Flow

Callers pass fs paths or strings and receive strings/vectors/maps filled from mergerfs control xattrs.

## State and Persistence Behavior

The file has 52 source lines and 1477 bytes. Its direct include set is: `fs_path.hpp`, `map`, `string`, `vector`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

It is used by diagnostic tools and should preserve errno-style negative return contracts.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
