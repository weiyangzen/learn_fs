# sources/user-network-fs/mergerfs/src/resources.hpp

## Purpose
Declares process resource helper functions.

## Important APIs, Types, and Functions
The `resources` namespace exports `reset_umask()`, `maxout_rlimit(int)`, `maxout_rlimit_nofile()`, `maxout_rlimit_fsize()`, and `setpriority(int)`.

## Control Flow
The header has no runtime flow; callers use the declarations during startup or tuning.

## State and Persistence Behavior
The declared functions mutate process resource state when implemented.

## Dependencies and Integration Points
The header is intentionally small and depends only on function declarations. It integrates with mergerfs initialization code.

## Risks and Edge Cases
Callers must handle negative errno-style returns from implementations.

## Test Signals
Build coverage and startup tests should confirm declarations match implementation and error returns are honored.
