<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFSctl.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFSctl.cc

## Purpose

`XrdPfcFSctl.cc` implements the filesystem-control plugin adapter that exposes cache management commands such as eviction and cached-state checks through XRootD FSctl.

## Important APIs, Types, And Functions

- `XrdPfcFSctl::XrdPfcFSctl()` stores the cache reference, logger, trace pointer, and trace id.
- `Configure()` obtains `XrdOfsHandle*` from the environment for hiding evicted paths.
- File-based `FSctl()` rejects all file-specific commands as unsupported.
- Base `FSctl()` handles `SFS_FSCTL_PLUGXC` commands `evict`, `fevict`, and `cached`.

## Control Flow

The base command path first verifies that the command is a plugin cache command and that an argument exists. `evict` and `fevict` require the special argument form (`Arg2Len == -2`), call `Cache::UnlinkFile()`, translate cache return codes to SFS return/error values, and hide the path from the OFS handle on success. `cached` calls `Cache::ConsiderCached()` and returns OK only when the cache considers the path sufficiently cached.

## State And Persistence

`evict`/`fevict` can persistently remove cache data and `.cinfo` metadata via `UnlinkFile()`. Successful eviction also updates OFS handle visibility through `Hide()`. `cached` is read-only except for any metadata/stat side effects inside cache checks.

## Dependencies And Integration Points

It depends on `XrdOfsHandle`, `XrdOucEnv`, `XrdOucErrInfo`, `XrdOucCache`, `XrdPfc::Cache`, `XrdPfcTrace`, `XrdSfsInterface`, and `XrdSysTrace`. `XrdOucGetCache()` installs an instance into the environment as `XrdFSCtl_PC*`.

## Risks And Edge Cases

- The code logs `rc=` and `ec=` with the same `ec` value, reducing diagnostic clarity.
- The `cached` command is checked after the eviction branch; invalid forms can flow through earlier error setup before cached handling.
- `Configure()` ignores config parameters and plugin set except for handle lookup.
- File-based FSctl is categorically unsupported.

## Test Signals

Tests should cover missing handle configuration, unsupported file FSctl, wrong command id, missing arguments, `evict` success/ENOENT/EBUSY/EAGAIN/default failures, forced `fevict`, path hiding on success, and `cached` success/failure mapping to `SFS_OK`/`SFS_ERROR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFSctl.cc -->
