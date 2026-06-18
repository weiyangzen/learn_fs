# sources/user-network-fs/mergerfs/src/mergerfs.cpp

## Purpose

This is the primary executable entry point and app multiplexer for mergerfs, fsck.mergerfs, and mergerfs.collect-info.

## Important APIs, Types, and Functions

types/namespaces: `fuse_operations`; functions: `FUSE::access`, `FUSE::bmap`, `FUSE::chmod`, `FUSE::chown`, `FUSE::copy_file_range`, `FUSE::create`, `FUSE::destroy`, `FUSE::fallocate`, `FUSE::fchmod`, `FUSE::fchown`

## Control Flow

It builds `fuse_operations`, parses options, waits for branches, configures resources/capabilities/OOM score/signal handlers, optionally lazy-unmounts the mountpoint, and enters `fuse_main`.

## State and Persistence Behavior

The file has 398 source lines and 9809 bytes. Its direct include set is: `mergerfs.hpp`, `mergerfs_fsck.hpp`, `mergerfs_collect_info.hpp`, `caps.hpp`, `config.hpp`, `fs_path.hpp`, `fs_readahead.hpp`, `fs_umount2.hpp`, `fs_wait_for_mount.hpp`, `maintenance_thread.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State centers on global `cfg`, libfuse arguments, syslog, process resource limits, and capability/OOM side effects.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
