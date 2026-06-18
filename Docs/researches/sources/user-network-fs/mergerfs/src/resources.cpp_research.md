# sources/user-network-fs/mergerfs/src/resources.cpp

## Purpose
Provides process resource setup helpers for mergerfs startup and runtime tuning.

## Important APIs, Types, and Functions
`resources::reset_umask()` clears the umask. `maxout_rlimit()`, `maxout_rlimit_nofile()`, and `maxout_rlimit_fsize()` raise resource limits. `resources::setpriority()` applies a nice value to the process and all current `/proc/self/task` threads.

## Control Flow
Limit raising first tries `RLIM_INFINITY`, then falls back to current hard limit and repeatedly doubles until `setrlimit()` fails. Priority setting calls `setpriority()` for pid 0, scans task ids, parses numeric entries, and sets each thread priority.

## State and Persistence Behavior
Changes are process-global resource and scheduling state. No files are persisted, but `/proc/self/task` is read.

## Dependencies and Integration Points
Uses POSIX resource APIs, procfs task layout, and mergerfs directory wrappers. Startup code can call these helpers before servicing FUSE requests.

## Risks and Edge Cases
The doubling loop can overflow `rlim_t` on unusual platforms. Priority failures are ignored for individual threads. The code assumes `/proc/self/task` exists.

## Test Signals
Test nofile/fsize calls under constrained users, umask reset, priority changes with multiple threads, and behavior when `/proc` is unavailable.
