# sources/user-network-fs/mergerfs/src/policy_msplfs.cpp

## Purpose
Implements `msplfs`: a path-preserving create policy that walks up the requested path and chooses the eligible branch with the least free space among branches where the nearest existing parent path exists.

## Important APIs, Types, and Functions
`_create_1()` searches one `fusepath` level and returns the candidate with minimum `info.spaceavail`. `_create()` repeatedly calls `_create_1()` while replacing the path with its parent until a candidate is found or `/` is reached. Action/search delegate to `eplfs`.

## Control Flow
The create flow preserves locality by first requiring the full path or parent to exist on a branch. Only after no branch matches does it walk to a parent. Eligible branches must be writable, create-capable, not readonly at statvfs time, and above `minfreespace`.

## State and Persistence Behavior
All state is local to branch scanning. Persistence is the eventual caller-created object on the chosen branch.

## Dependencies and Integration Points
Uses `fs_exists`, `fs_info`, `fs_path`, `policy_error`, and `Policies::{Action,Search}::eplfs`. It integrates with path-preserving create policies that prefer existing directory topology.

## Risks and Edge Cases
The code includes `fs_statvfs_cache.hpp` but uses `fs::info()`, so cache expectations should be checked elsewhere. Equal free-space ties prefer later branches, and parent walking can select a less-specific ancestor when the exact path is absent.

## Test Signals
Test exact path hits, parent fallback, root fallback failure, least-free tie behavior, ro/nc/min-free filtering, and action/search consistency with `eplfs`.
