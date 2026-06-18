# sources/user-network-fs/mergerfs/src/mergerfs_ioctl.hpp

## Purpose

This header defines the mergerfs ioctl buffer contract.

## Important APIs, Types, and Functions

types/namespaces: `mergerfs_ioctl_t`

## Control Flow

`MERGERFS_IOCTL_BUF_SIZE` is 256 KiB and `mergerfs_ioctl_t` packs a version, size, and remaining char buffer for ioctl payloads.

## State and Persistence Behavior

The file has 45 source lines and 1383 bytes. Its direct include set is: `base_types.h`, `sys/ioctl.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

Consumers must keep size/version validation strict because ioctl payloads cross process/kernel-facing boundaries.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
