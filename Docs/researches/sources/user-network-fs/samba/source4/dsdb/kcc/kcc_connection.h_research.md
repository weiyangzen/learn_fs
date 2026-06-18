# sources/user-network-fs/samba/source4/dsdb/kcc/kcc_connection.h

## Purpose

`kcc_connection.h` defines lightweight connection records and lists used by KCC connection reconciliation.

## Important APIs, Types, and Functions

- `struct kcc_connection` contains the connection object's GUID (`obj_guid`), source DSA GUID (`dsa_guid`), invocation ID, and an 84-byte schedule buffer.
- `struct kcc_connection_list` contains a count and dynamically allocated array of `struct kcc_connection`.

No functions are declared in this header; functions are implemented in `kcc_connection.c` and made visible through other local prototype generation.

## Control Flow

The header does not implement control flow. Its structures are populated by `kccsrv_find_connections()` and consumed by `kccsrv_apply_connections()`.

## State and Persistence Behavior

The structures are in-memory projections of persisted `nTDSConnection` objects or desired topology state. `obj_guid` identifies existing connection objects; `dsa_guid` identifies source DSAs used for matching. The `schedule` field is currently not persisted by the add path in this subset.

## Dependencies and Integration Points

It relies on `struct GUID` being available from including compilation units. It is included by KCC service code that computes and applies topology.

## Risks

The header does not record whether a connection is generated or administrator-created, which contributes to the reconciliation risk noted in `kcc_connection.c`. Future fixes may need to extend this structure with option flags or provenance.

## Test Signals

Tests should indirectly validate structure use through connection discovery and reconciliation. Static analysis should ensure callers initialize all fields they compare or persist.
