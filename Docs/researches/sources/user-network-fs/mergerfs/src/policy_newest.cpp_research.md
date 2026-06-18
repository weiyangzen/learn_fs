# sources/user-network-fs/mergerfs/src/policy_newest.cpp

## Purpose
Implements the `newest` policy, selecting the branch whose matching path has the newest modification time. It supports create, action, and search variants with different writeability checks.

## Important APIs, Types, and Functions
`_create()` finds the newest existing path among writable/create-capable branches and checks free space. `_action()` finds the newest writable existing path using `fs::statvfs_cache_readonly()`. `_search()` returns the newest existing path without writeability filtering.

## Control Flow
Each function scans branches, calls `fs::exists()` with `struct stat`, compares `st_mtime`, and stores the best branch. Create also calls `fs::info()` and enforces `minfreespace`; action checks branch and filesystem read-only state; search only requires existence.

## State and Persistence Behavior
No persistent state is kept. The selected newest branch controls which backing object is read, modified, or chosen for a path-preserving create.

## Dependencies and Integration Points
Uses `fs_exists`, `fs_info`, `fs_statvfs_cache`, `policy_error`, and POSIX `stat`. It integrates with policies that need temporal resolution of duplicate files.

## Risks and Edge Cases
Only second-resolution `st_mtime` is considered, so equal mtimes prefer later branches. Newest create requires the path already exists somewhere; missing paths return `ENOENT`. Cached readonly state can differ from fresh statvfs state.

## Test Signals
Test duplicate files with ordered mtimes, equal mtime tie behavior, create low-space errors, action on readonly branches, search on read-only branches, and missing paths.
