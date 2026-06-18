# sources/user-network-fs/nfs-utils/support/include/fsloc.h

## Purpose
Declares the simple NFSv4 fs_locations representation used by export option parsing.

## Important APIs, Types, and Functions
`FSLOC_MAX_LIST`, `struct mount_point`, `struct servers`, `replicas_lookup()`, and `release_replicas()`.

## Control Flow
Callers pass a method and location string to `replicas_lookup()`, then serialize returned mount points to kernel export cache data and release them.

## State and Persistence Behavior
Returned structures own heap strings and are not persisted directly. Export options remain the durable source.

## Dependencies and Integration Points
Implemented by `support/export/fsloc.c` and consumed by export cache writers.

## Risks and Edge Cases
Fixed maximum list size can truncate large location sets. `h_referral` is an int flag whose meaning must be preserved.

## Test Signals
Test refer/replica method parsing, empty/invalid data, maximum list size, and release cleanup.
