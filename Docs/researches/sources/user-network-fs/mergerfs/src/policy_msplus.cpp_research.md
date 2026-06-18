# sources/user-network-fs/mergerfs/src/policy_msplus.cpp

## Purpose
Implements `msplus`: a most-shared-path create policy that selects the branch with the least used space among eligible branches sharing the target path or nearest existing parent.

## Important APIs, Types, and Functions
`_create_1()` checks one fuse path level and chooses the minimum `info.spaceused`. `_create()` climbs parent paths until a candidate is found. The public policy methods route action/search to `eplus`.

## Control Flow
Create begins at the requested path, filters branches without that path, branches that are read-only/no-create, stat failures, readonly filesystems, and branches below `minfreespace`. If none match, it repeats for the parent path until `/`.

## State and Persistence Behavior
The implementation is stateless and local. The persistent side effect is delegated to the caller that creates an object on the returned branch.

## Dependencies and Integration Points
Depends on `fs_exists`, `fs_info`, `fs_path`, `policy_error`, and common `Policies::Action/Search::eplus` helpers.

## Risks and Edge Cases
Parent fallback may surprise users expecting non-path-preserving least-used behavior. Equal used-space ties keep the earlier candidate because `>=` skips later equal branches. Race windows exist between path existence checks and creation.

## Test Signals
Cover exact and parent path matching, least-used selection, no eligible branch errno propagation, readonly/min-free filters, and equality/tie cases.
