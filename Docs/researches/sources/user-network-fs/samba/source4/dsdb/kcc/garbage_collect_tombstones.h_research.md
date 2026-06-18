# sources/user-network-fs/samba/source4/dsdb/kcc/garbage_collect_tombstones.h

## Purpose

`garbage_collect_tombstones.h` declares the public tombstone garbage collection entry point used by KCC and administrative tools.

## Important APIs, Types, and Functions

- `dsdb_garbage_collect_tombstones()` accepts a memory context, samdb connection, linked list of naming-context partitions, current Unix time, tombstone lifetime in days, output counters for removed objects and links, and an output error string.

## Control Flow

The header only declares the API. Callers provide the partition list and timing inputs; the implementation handles schema-driven search, object deletion, and expired linked-value cleanup.

## State and Persistence Behavior

The declared function mutates DSDB persistent state by deleting expired tombstones and vanished link values. Output counters are reset and populated by the implementation, and `error_string` is set on certain fatal failures.

## Dependencies and Integration Points

The header includes Samba parameter, samdb, and DSDB utility headers so the partition list and LDB types are visible. It is implemented by `garbage_collect_tombstones.c` and called from KCC maintenance and tooling.

## Risks

The signature exposes destructive behavior without an explicit transaction handle or dry-run flag. Callers must ensure `current_time`, `tombstoneLifetime`, and partition scope are correct. Output pointers must be non-NULL as the implementation writes through them immediately.

## Test Signals

Compile tests should confirm callers see the declaration. Integration tests should invoke the function with controlled partitions and validate object/link removal counters and error-string behavior.
