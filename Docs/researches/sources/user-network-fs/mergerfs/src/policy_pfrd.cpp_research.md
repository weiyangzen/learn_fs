# sources/user-network-fs/mergerfs/src/policy_pfrd.cpp

## Purpose
Implements `pfrd`, proportional free-space random distribution for create operations across all eligible branches. Action and search use existing-path proportional helpers.

## Important APIs, Types, and Functions
`BranchInfo` records `spaceavail` and `Branch*`. `_get_branchinfo()` filters branches and sums free space. `_get_branch()` draws a random value using `RND::rand64(sum)` and chooses by cumulative weight. `_create()` coordinates these helpers.

## Control Flow
Create scans all branches once, rejecting read-only/no-create, stat failures, readonly filesystems, and branches below `minfreespace`. If the summed available space is nonzero, the branch selection is weighted by each branch's free space.

## State and Persistence Behavior
Only local vectors and the global RNG seed are used. Later create code performs the persistent filesystem mutation.

## Dependencies and Integration Points
Depends on `fs_info`, `policy_error`, `rnd.hpp`, and `Policies::*::eppfrd`. It is intended for balancing writes probabilistically rather than deterministically.

## Risks and Edge Cases
Distribution correctness depends on RNG quality and threshold boundary handling. Very large free-space sums could overflow `u64` if many huge branches are aggregated. Branch state can change between selection and create.

## Test Signals
Run repeated-create distribution checks, zero-sum and all-filtered branch cases, min-free/read-only filtering, and action/search behavior with duplicate paths.
