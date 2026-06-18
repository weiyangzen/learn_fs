# sources/distributed-fs/xrootd/src/XrdOss/XrdOssRename.cc

## Purpose
Implements OSS rename semantics for local files, cache symlinks, and remote/MSS-backed files while enforcing compatible export options.

## Important APIs, types, and functions
`XrdOssSys::Rename()` checks write permissions/export flags for old and new names, rejects renames across incompatible remote/migration attributes, generates local and optional remote paths, prevents overwriting remote or symlink targets, creates parent directories, renames either a normal local path or a symlink-backed cache file, then mirrors the rename to MSS when appropriate. `RenameLink()` handles symlink targets: for XA cache targets ending in `%`, it calls `RenameLink3()` and may adjust solitary usage for offline `.anew` stage-ins; for old-style targets it converts the target with `XrdOssPath::Convert()`, creates the new logical symlink, renames the real PFN, and unlinks the old logical path. `RenameLink3()` updates the PFN xattr to the new logical path before renaming the symlink and restores the old attribute if rename fails.

## Control flow
The local rename runs first. Remote rename is attempted only for remote exports and when local rename succeeded or the local path was missing. Symlink-specific flow preserves cache target integrity and xattrs.

## State and persistence
Renames local files/symlinks, old-style real PFNs, remote MSS paths, and PFN xattrs. It may create destination parent directories. In solitary usage mode, it adjusts cache usage when an offline `.anew` link becomes visible.

## Dependencies and integration points
Uses `Check_RO`, `GenLocalPath`, `GenRemotePath`, `MSS_Rename`, `XrdOssPath`, `XrdSysFAttr`, `XrdFrcXAttrPfn`, and export flags from `XrdOucExport`.

## Risks and test signals
Remote/local consistency can diverge if MSS rename fails after local rename. Symlink overwrite prevention is stricter than normal local rename. Tests should cover remote-only/local-only incompatibility, old-style and XA cache symlink renames, xattr rollback failure, existing destination handling, parent path creation, and solitary `.anew` usage adjustment.
