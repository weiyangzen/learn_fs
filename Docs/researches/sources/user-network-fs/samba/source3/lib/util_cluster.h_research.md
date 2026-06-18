<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_cluster.h -->
# sources/user-network-fs/samba/source3/lib/util_cluster.h

## Purpose
This header declares the source3 cluster utility probe API.

## Important APIs, types, and functions
It exposes `bool cluster_probe_ok(void)`.

## Control flow
Callers use the function as a startup or preflight predicate before assuming CTDB-backed clustering is available.

## State and persistence behavior
The header has no state.

## Dependencies and integration points
It isolates users from CTDB-specific include requirements in `util_cluster.c`.

## Risks and edge cases
The boolean return hides probe details; callers needing diagnostics must rely on logging from the implementation.

## Test signals
Compile coverage verifies the declaration. Functional tests belong to `util_cluster.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_cluster.h -->
