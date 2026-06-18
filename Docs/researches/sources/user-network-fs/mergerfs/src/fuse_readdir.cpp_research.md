# sources/user-network-fs/mergerfs/src/fuse_readdir.cpp

## Purpose

`fuse_readdir.cpp` implements the mergerfs FUSE `readdir` callback. It dispatches directory listing to a runtime-selected sequential or concurrent readdir strategy.

## Important APIs, Types, and Functions

functions: `FUSE::ReadDir`, `FUSE::ReadDirBase`, `FUSE::ReadDirFactory`, `FUSE::readdir`

## Control Flow

cfg.readdir invokes ReadDir, which swaps implementations under a shared mutex, delegates to ReadDirBase, and converts root ENOENT into a synthetic diagnostic dirent

## State and Persistence Behavior

The file has 143 source lines and 2971 bytes. Its direct include set is: `fuse_readdir.hpp`, `fuse_readdir_factory.hpp`, `dirinfo.hpp`, `fatal.hpp`, `fuse_dirents.hpp`, `config.hpp`, `cstring`, `dirent.h`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: ReadDir::_impl, _str, _initialized, DirInfo fusepath, and cfg.readdir. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
