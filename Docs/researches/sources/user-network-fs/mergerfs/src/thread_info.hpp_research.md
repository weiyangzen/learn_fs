# sources/user-network-fs/mergerfs/src/thread_info.hpp

## Purpose
Provides a small helper for estimating current process thread count.

## Important APIs, Types, and Functions
`thread_info::process_count()` calls `fs::lstat("/proc/self/task", &st)` and returns `st.st_nlink - 2`.

## Control Flow
The helper returns a negative errno-style result if `lstat` fails; otherwise it derives count from procfs link count.

## State and Persistence Behavior
No state is retained and no files are modified.

## Dependencies and Integration Points
Depends on `fs_lstat.hpp` and Linux procfs semantics. It can feed diagnostics or resource decisions.

## Risks and Edge Cases
The link-count heuristic is Linux/procfs-specific and may be inaccurate in unusual environments. Return type is `int` while link count is wider.

## Test Signals
Test single-thread and multi-thread counts on Linux, plus failure behavior when procfs is unavailable.
