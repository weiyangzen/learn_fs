<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirState.cc -->
# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirState.cc

## Purpose

`XrdPfcDirState.cc` implements the in-memory directory tree used by XrdPfc resource monitoring to track per-directory cache usage and IO statistics, propagate child usage upward, remove empty leaf directories, reset interval counters, and dump diagnostic views.

## Important APIs, Types, And Functions

- `DirState` constructors create root or child nodes with parent/depth metadata.
- `create_child()`, `find_path_tok()`, `find_path()`, and `find_dir()` manage tree lookup and optional creation.
- `generate_dir_path()` reconstructs an absolute path from parent links.
- `upward_propagate_initial_scan_usages()` folds initial child usage into parent recursive usage.
- `update_stats_and_usages()` recursively accumulates stats, updates usage counters, and optionally unlinks/erases empty leaf directories.
- `reset_stats()`, `reset_sshot_stats()`, `count_dirs_to_level()`, and `dump_recursively()` support resource monitor intervals and diagnostics.
- `DataFsState` wrappers drive root-level update, reset, and dump operations with timestamps.

## Control Flow

Path lookup tokenizes a path with `PathTokenizer`, descends one component at a time, and optionally creates missing nodes. Updates run post-order: children update first, then parent recursive stats/usages are accumulated. Empty directory purge only removes leaf nodes whose current stats/usages indicate no files or subdirectories and whose unlink callback succeeds.

## State And Persistence

`DirState` stores current interval stats, recursive subdir stats, current usage, recursive usage, snapshot stats, parent pointer, child map, depth, and scan status. Persistent effects are indirect: `update_stats_and_usages()` can call an injected unlink function to remove empty directories from the underlying namespace.

## Dependencies And Integration Points

It depends on `XrdPfcDirState.hh`, `XrdPfcPathParseTools.hh`, `DirStats`, and `DirUsage`. It is used by `XrdPfcResourceMonitor` and snapshot/purge representations.

## Risks And Edge Cases

- Recursive traversal over deep directory trees can be expensive and stack-heavy.
- `generate_dir_path()` relies on parent links and root naming assumptions; root returns an empty prefix.
- Empty-directory purge intentionally removes only one level at a time, so repeated updates may be needed.
- Stats reset and update ordering must be coordinated by the resource monitor lock discipline.

## Test Signals

Tests should cover path creation, max-depth tokenization, last-existing-dir reporting, initial scan propagation, update propagation, empty leaf unlink success/failure, snapshot stats reset, counting by depth, and generated paths for root and nested directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcDirState.cc -->
