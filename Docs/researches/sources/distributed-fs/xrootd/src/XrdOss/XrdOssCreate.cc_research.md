# sources/distributed-fs/xrootd/src/XrdOss/XrdOssCreate.cc

## Purpose
Implements `XrdOssSys::Create()`, including local creation, cache-space allocation, remote-storage prechecks/creates, stage-command routing for creates, colocation, symlink creation for cache PFNs, and copy-time/PFN xattr setup.

## Important APIs, types, and functions
`XrdOssCreateInfo` carries path, LFN, mode, create options, and resolved export flags. `Create()` checks path writability via `Check_RO`, generates the local path, handles dangling symlinks, processes `XRDOSS_coloc` by resolving `oss.coloc` into a cache group/path, routes missing-file creates to `Stage()` when `StageCreate` is enabled, reopens existing files unless `XRDOSS_new` is set, creates parent directories for `XRDOSS_mkpath`, validates/creates MSS-side files for remote exports, and chooses `Alloc_Cache()` or `Alloc_Local()`. `Alloc_Cache()` parses `oss.asize` and `oss.cgroup`, applies `SPList` assign/default rules, calls `XrdOssCache::Alloc()`, sets the PFN xattr, sets copy-time metadata, and symlinks the logical path to the cache PFN. `Alloc_Local()` creates a normal local file. `SetFattr()` records `XrdFrcXAttrCpy` ctime where migration xattrs are enabled.

## Control flow
Existing paths short-circuit through open/truncate/xattr handling. Missing paths can go through remote checks, cache allocation, or local allocation. Cache allocation creates a hidden PFN first, then atomically replaces/creates the logical symlink; failures unlink the PFN where possible.

## State and persistence
Creates files, directories, symlinks, remote MSS entries, xattrs, and cache free-space reservations. If xattrs are unsupported, it marks the export path `XRDEXP_NOXATTR` through `RPList`. Truncating a symlink-backed existing file adjusts cache accounting.

## Dependencies and integration points
Integrates with `XrdOssCache`, `XrdOssPath`, `XrdOssSpace`, `XrdOucEnv`, `XrdOucExport`, `XrdFrcXAttr`, `XrdSysFAttr`, remote MSS helpers, and the global `XrdOssSS` staging interface. Opaque env keys from `XrdOssOpaque.hh` drive allocation size, cache group, and colocation.

## Risks and test signals
High-risk paths include dangling symlink cleanup, colocation URL decoding, remote/local consistency when MSS create succeeds but local allocation fails, PFN xattr failure, xattr unsupported fallback, and symlink replacement races. Tests should cover new/existing/truncate, mkpath, StageCreate, RCREATE/NOCHECK combinations, cache and non-cache exports, forced colocation, ENOSPC, and unsupported xattrs.
