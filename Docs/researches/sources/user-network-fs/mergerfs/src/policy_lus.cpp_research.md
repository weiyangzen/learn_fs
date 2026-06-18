# sources/user-network-fs/mergerfs/src/policy_lus.cpp

## Purpose
Implements the `lus` create policy, choosing the writable branch with the least used space among all eligible branches. Action and search behavior delegates to existing-path `eplus` helpers.

## Important APIs, Types, and Functions
The private `_create()` scans `Branches`, calls `fs::info()`, checks `Branch::ro_or_nc()`, `info.readonly`, and `Branch::minfreespace()`, then appends the branch with the smallest `info.spaceused`. `Policy::LUS::{Action,Create,Search}::operator()` expose the policy interface.

## Control Flow
Create starts with `ENOENT` as the fallback error, filters read-only, no-create, missing/stat-failed, and low-space branches, and keeps the best branch by `spaceused`. If no branch survives, it returns the most relevant negative errno. Action/search call `Policies::Action::eplus()` and `Policies::Search::eplus()`.

## State and Persistence Behavior
The function keeps only local scan state. Persistent effects happen in callers that use the selected branch to create files or route operations.

## Dependencies and Integration Points
It integrates with `fs_info`, `policy_error`, `Branches`, and the shared `Policies::*::eplus` existing-path strategy.

## Risks and Edge Cases
Ties prefer the later branch because equal `spaceused` is skipped only when current usage is greater or equal. Space values depend on fresh `fs::info()` calls, so concurrent filesystem changes can alter placement between selection and create.

## Test Signals
Exercise branch ordering on ties, ro/nc filtering, min-free-space rejection, stat failure fallback, and search/action parity with `eplus`.
