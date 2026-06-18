# sources/user-network-fs/mergerfs/src/fuse_open.cpp

## Purpose

`fuse_open.cpp` implements the mergerfs FUSE `open` callback. It opens existing files through the configured search policy, creates per-handle FileInfo objects, coordinates shared open-file state by nodeid, and optionally installs Linux FUSE passthrough backing IDs.

## Important APIs, Types, and Functions

types/namespaces: `stat`, `timespec`; functions: `FUSE::open`, `FUSE::passthrough_close`, `FUSE::passthrough_open`, `FUSE::release`

## Control Flow

select a branch, adjust cache/writeback flags, break copy-on-write links when configured, open or duplicate a canonical fd, insert or visit state.open_files, and unwind fd/backing resources on races

## State and Persistence Behavior

The file has 493 source lines and 13906 bytes. Its direct include set is: `fuse_open.hpp`, `state.hpp`, `config.hpp`, `errno.hpp`, `fileinfo.hpp`, `fuse_release.hpp`, `fs_close.hpp`, `fs_cow.hpp`, `fs_fchmod.hpp`, `fs_lchmod.hpp`. Persistent effects, when present, occur through configured branch filesystems, libfuse handles, process-global `cfg`/state objects, procfs, or command output files rather than through private long-lived storage in this file.

## Dependencies and Integration Points

This file is integrated through the mergerfs FUSE operation table, policy registry, command dispatch, or utility headers depending on its role. It uses the local `fs_*` wrappers, `config.hpp`, policy abstractions, and libfuse-facing types so callers receive negative errno values instead of raw system-call conventions.

## Risks and Edge Cases

State and persistence: state.open_files refcounts, FileInfo ownership, fuse_file_info flags and backing_id, cfg cache/passthrough/nfsopenhack/link_cow settings. Risks include errno compatibility with libfuse, stale handles or branch paths, and behavior changes in configured policies. Test signals should exercise success, negative errno paths, branch-policy edge cases, and FUSE handle lifetime.

## Test Signals

Useful tests are targeted unit tests around branch selection and errno folding, integration tests against a mounted mergerfs instance, and regression tests for configured options that change behavior. For this file specifically, assert the declared APIs stay ABI-compatible with their callers, negative errno paths are preserved, and stateful resources are released exactly once.
