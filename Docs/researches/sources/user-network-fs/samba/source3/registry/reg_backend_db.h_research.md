# sources/user-network-fs/samba/source3/registry/reg_backend_db.h

## Purpose

`reg_backend_db.h` declares lifecycle and transaction functions for Samba’s default registry TDB backend.

## Important APIs, Types, and Functions

- `init_registry_key()` and `init_registry_data()` initialize built-in registry structure.
- `regdb_init()`, `regdb_open()`, and `regdb_close()` manage the singleton DB context.
- `regdb_transaction_start()`, `regdb_transaction_commit()`, and `regdb_transaction_cancel()` expose transaction control.
- `regdb_get_seqnum()` returns the backend sequence number used by caches.

## Control Flow

Callers initialize or open the backend before registry operations, use transactions around multi-step mutations, and close handles when registry key objects are freed.

## State and Persistence

The header does not store state. The implementation manages `registry.tdb`, a DB context, and a refcount.

## Dependencies and Integration Points

It includes `registry.h` for WERROR and registry types. `reg_api.c` uses the lifecycle and transaction functions; backend setup code uses initialization functions.

## Risks and Edge Cases

Callers must pair opens with closes and must not assume transactions are active unless start returned `WERR_OK`.

## Test Signals

Compile-time checks plus integration tests around registry open/create/set/delete transaction paths validate this interface.
