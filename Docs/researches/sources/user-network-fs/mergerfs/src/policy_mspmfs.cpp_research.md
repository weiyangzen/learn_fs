# sources/user-network-fs/mergerfs/src/policy_mspmfs.cpp

## Purpose
Implements `mspmfs`, a path-preserving variant of most-free-space creation. It picks the branch with the largest available space among branches containing the target path or nearest existing parent.

## Important APIs, Types, and Functions
`_create_1()` scans eligible branches for one path level and returns the maximum `info.spaceavail` candidate. `_create()` performs parent fallback. Public `Action`, `Create`, and `Search` methods bridge to `epmfs` helpers or local create logic.

## Control Flow
The create routine searches the exact path first, then climbs to parents until a branch is found or root is exhausted. Branch filters enforce read/write availability, create permission, stat success, and `minfreespace`.

## State and Persistence Behavior
No state is retained. Branch choice drives the later persistent file or directory placement.

## Dependencies and Integration Points
It depends on branch metadata, `fs::exists()`, `fs::info()`, and `Policies::*::epmfs`, tying it to mergerfs category.create and existing-path operation routing.

## Risks and Edge Cases
Tie handling favors later branches because equal or larger free space replaces the winner. Parent traversal can route new files according to an ancestor directory rather than the requested leaf.

## Test Signals
Validate parent fallback, branch choice by free space, read-only/no-create/min-free rejection, and action/search behavior for existing files.
