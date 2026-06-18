# sources/user-network-fs/samba/source4/ntvfs/common/brlock.h

## Purpose

`brlock.h` defines the backend operations interface for source4 NTVFS byte-range locking and declares backend selection helpers.

## Important APIs, Types, and Functions

The central type is `struct brlock_ops`, containing function pointers for init, handle creation, lock, unlock, pending-lock removal, lock tests, close cleanup, and count. It declares `brlock_set_ops()` and `brl_tdb_init_ops()`.

## Control Flow

The header has no runtime flow, but it defines the dispatch contract implemented by `brlock_tdb.c` and consumed by `brlock.c`.

## State and Persistence Behavior

The interface abstracts backend state in `struct brl_context` and `struct brl_handle`. Callers treat those as opaque and rely on the backend to persist or remove byte-range lock records.

## Dependencies and Integration Points

It includes `libcli/libcli.h` for `NTSTATUS` and lock-type declarations, and is included through `ntvfs_common.h` by NTVFS common users.

## Risks and Edge Cases

ABI is internal but pointer signatures must remain synchronized with wrappers and backends. The interface exposes raw `void *notify_ptr` for pending-lock notifications, so callers and backends must agree on lifetime and messaging semantics.

## Test Signals

Compile-time tests should catch signature drift. Runtime tests should exercise every ops slot through the public wrapper and verify pending notification pointer round trips.
