# sources/user-network-fs/nfs-utils/support/export/xtab.c

## Purpose
Reads and writes the etab export-state file and manages paths under the nfs-utils state directory. It preserves mountd/exportfs shared state with locking and atomic replacement.

## Important APIs, Types, and Functions
Public APIs are `xtab_export_read()`, `xtab_export_write()`, `state_setup_basedir()`, `setup_state_path_names()`, and `free_state_path_names()`. Internal helpers are `xtab_read()`, `xtab_write()`, `cond_rename()`, and `state_make_pathname()`.

## Control Flow
`xtab_read()` locks etab for reading, parses export entries, creates or updates in-core exports, marks `m_xtabent` and `m_mayexport`, and disables dynamic v4root generation when fsid 0 is present. `xtab_write()` writes marked exports to a temp file using canonical client hostnames, then renames only if content differs.

## State and Persistence Behavior
Persists export state in `etab.statefn`, `etab.tmpfn`, and `etab.lockfn`, all derived from `state_base_dirname`. `v4root_needed` is process-global. File replacement intentionally changes inode when content changes for auth reload detection.

## Dependencies and Integration Points
Depends on `nfslib.h` parser/writer functions, `xio` locks, `exportfs.h`, `v4root.h`, `misc.h` path helpers, and state directory macros. Used by mountd/exportfs state synchronization.

## Risks and Edge Cases
Parser cleanup manually frees selected fields after `getexportent()`. `cond_rename()` ignores some open/read errors. State setup runs before logging and reports to stderr. Content-identical writes unlink temp files and do not refresh inode.

## Test Signals
Test read/write locking, fsid 0 v4root detection, malformed entries, temp rename with identical and changed files, missing state dir, long path names, and auth reload behavior tied to etab inode replacement.
