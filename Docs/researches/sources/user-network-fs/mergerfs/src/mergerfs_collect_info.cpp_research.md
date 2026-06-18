# sources/user-network-fs/mergerfs/src/mergerfs_collect_info.cpp

## Purpose

This diagnostic command gathers support information into `/tmp/mergerfs.info.txt`.

## Important APIs, Types, and Functions

functions: `mergerfs::collect_info::main`

## Control Flow

It appends command headers/output for version, uname, lsb_release, df, lsblk, mounts, branch stat data, mergerfs settings, fstab, container/Samba versions, lshw, and recent journal entries.

## State and Persistence Behavior

The file has 243 source lines and 5136 bytes. Its direct include set is: `mergerfs_collect_info.hpp`, `mergerfs_api.hpp`, `fs_mounts.hpp`, `fs_unlink.hpp`, `CLI11/CLI11.hpp`, `fmt/core.h`, `fmt/ranges.h`, `scope_guard/scope_guard.hpp`, `subprocess/subprocess.hpp`, `stdio.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

The command has host-inspection and privacy implications; tests can mock subprocess failures and verify output sections are appended safely.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
