# sources/user-network-fs/mergerfs/src/policy_msppfrd.cpp

## Purpose
Implements `msppfrd`, combining most-shared-path parent matching with proportional free-space random distribution. Eligible branches are weighted by available space.

## Important APIs, Types, and Functions
`BranchInfo` stores `spaceavail` and a `Branch*`. `_create_1()` collects branch weights for a path level. `_get_branchinfo()` performs parent fallback. `_get_branch()` draws a random threshold with `RND::rand64(sum)` and selects by cumulative weight.

## Control Flow
Create collects candidates from the requested path or nearest existing parent, rejects unavailable branches, sums available space, and randomly chooses a branch with probability proportional to free space. Action/search delegate to `eppfrd`.

## State and Persistence Behavior
The implementation has no persisted state, but it consumes global RNG state through `RND`. The chosen branch determines where later create operations persist data.

## Dependencies and Integration Points
Depends on `fs_exists`, `fs_info`, `policy_error`, `rnd.hpp`, and proportional existing-path helpers in `Policies`.

## Risks and Edge Cases
Random threshold behavior at zero and boundaries must be tested carefully; `RND::rand64(sum)` returns `[0,sum)`, while selection uses `idx < threshold`. Candidate collection is not cleared across parent levels, though it stops at the first non-empty level.

## Test Signals
Use statistical tests for weighted distribution, deterministic mocks if available, parent fallback scenarios, zero-space rejection, and min-free/read-only filters.
