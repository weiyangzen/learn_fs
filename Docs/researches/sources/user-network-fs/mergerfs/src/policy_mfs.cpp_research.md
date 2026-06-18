# sources/user-network-fs/mergerfs/src/policy_mfs.cpp

## Purpose
Implements the `mfs` create policy, selecting the eligible branch with the most available space. Existing-path action and search calls use the `epmfs` helpers.

## Important APIs, Types, and Functions
`_create()` scans every `Branch`, obtains `fs::info_t`, checks read-only/no-create and `minfreespace`, and stores the branch with maximum `info.spaceavail`. `Policy::MFS::Action`, `Create`, and `Search` implement the policy interface.

## Control Flow
The create path has a single pass over branches. Each rejected branch updates the candidate error through `error_and_continue`; a valid branch replaces the winner when it has at least as much available space as the current maximum. Action/search delegate to `Policies::Action::epmfs()` and `Policies::Search::epmfs()`.

## State and Persistence Behavior
The implementation is stateless. The selected branch influences later filesystem persistence by choosing where a new object is placed.

## Dependencies and Integration Points
Depends on `fs_info.hpp`, `policy_error.hpp`, and shared policy helpers. It is used by category.create defaults in the Python parity harness.

## Risks and Edge Cases
The later branch wins equal-space ties. Available-space snapshots can become stale before the actual create operation, and low-space branches return `ENOSPC` only if no better branch is found.

## Test Signals
Validate most-free selection, tie behavior, read-only and min-free rejection, and parity of action/search with pre-existing files.
