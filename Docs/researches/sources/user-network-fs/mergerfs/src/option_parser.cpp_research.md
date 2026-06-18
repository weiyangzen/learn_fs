# sources/user-network-fs/mergerfs/src/option_parser.cpp

## Purpose

This file converts command-line/libfuse options and non-option operands into global mergerfs configuration.

## Important APIs, Types, and Functions

types/namespaces: `fuse_opt`, `options`

## Control Flow

It uses `fuse_opt_parse`, feeds recognized key/value options to `cfg.set`, interprets branch and mountpoint operands, adds default FUSE options, derives fsname/subtype, validates mount loops, warns about unsupported overrides, and normalizes passthrough-related settings.

## State and Persistence Behavior

The file has 352 source lines and 8635 bytes. Its direct include set is: `config.hpp`, `ef.hpp`, `errno.hpp`, `fmt/core.h`, `fs_glob.hpp`, `fs_path.hpp`, `fs_statvfs_cache.hpp`, `hw_cpu.hpp`, `num.hpp`, `policy.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State is global `cfg` and `fuse_cfg`; risks include operand ordering, passthrough/cache incompatibilities, and preserving unknown options for libfuse.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
