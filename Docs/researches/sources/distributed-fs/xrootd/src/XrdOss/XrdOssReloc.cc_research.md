# sources/distributed-fs/xrootd/src/XrdOss/XrdOssReloc.cc

## Purpose
Implements cache relocation/copying of an existing file to another cache group or partition, optionally anchoring a copy under a separate namespace path.

## Important APIs, types, and functions
`XrdOssSys::Reloc(tident, path, cgName, anchor)` is the sole exported operation. It uses a local `pendFiles` cleanup helper to close pending fds and unlink temporary PFNs/links on failure. It supports pure PFN relocation when `anchor` is `"."`, normal LFN relocation through `GenLocalPath()`, and copy-to-anchor mode when `anchor` is a base path. It parses target `cgName` through `XrdOssCache::Parse()`, gets current cache group/path from `XrdOssPath::getCname()`, allocates an XA target through `XrdOssCache::Alloc()`, copies data with `XrdOssCopy::Copy()`, creates a symlink to the target, atomically renames it over the original for relocation, and adjusts cache usage/free counters.

## Control flow
Relocation validates that the source exists and is a regular file, rejects no-op moves to the same group/path, allocates the target PFN, copies data, creates either an `.anew` replacement symlink or an anchored copy symlink, and finally removes/adjusts the old cache target when this was a move rather than a copy.

## State and persistence
Creates a new cache PFN, new symlink, and possibly removes the old PFN/symlink. Updates cache accounting for old and new locations through `XrdOssCache::Adjust()`. The cleanup object removes incomplete artifacts on early return.

## Dependencies and integration points
Depends on `XrdOssCache`, `XrdOssPath`, `XrdOssCopy`, `XrdOucUtils::makePath`, and global logging/tracing. It assumes XA cache spaces because it rejects allocations without `cgPsfx`.

## Risks and test signals
Important tests include no-op detection, pure PFN relocation, anchored copy preserving original, atomic replacement, cleanup on copy/symlink failure, old symlink target deletion, accounting deltas for old/new filesystems, and non-XA target rejection.
