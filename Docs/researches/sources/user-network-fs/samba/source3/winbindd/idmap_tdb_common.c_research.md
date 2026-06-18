# sources/user-network-fs/samba/source3/winbindd/idmap_tdb_common.c

## Purpose
This file provides shared allocation, storage, and lookup logic for TDB-like idmap backends. It supports high-water-mark allocation, bidirectional SID/UID/GID records, batch status aggregation, and optional allocation of missing SID mappings.

## Important APIs, Types, And Functions
Exported functions include `idmap_tdb_common_get_new_id`, `idmap_tdb_common_set_mapping`, `idmap_tdb_common_new_mapping`, `idmap_tdb_common_unixids_to_sids`, `idmap_tdb_common_unixid_to_sid`, `idmap_tdb_common_sid_to_unixid`, and `idmap_tdb_common_sids_to_unixids`. It expects `struct idmap_tdb_common_context` in `dom->private_data`.

## Control Flow
Allocation validates default domain `*`, selects UID or GID HWM key, and runs `idmap_tdb_common_allocate_id_action` in a dbwrap transaction. The action fetches HWM, range-checks, atomically increments, rechecks, and returns the allocated previous value. Mapping storage builds `SID` and `UID <id>` or `GID <id>` keys, checks for existing SID mapping, inserts both directions, and removes the first record if the reverse insert fails. Batch Unix-ID lookup initializes statuses, delegates each item to a hook or default function, and returns all/some/none status. Batch SID lookup first reads records, then if some are unmapped and the domain is writable, reruns inside a transaction with allocation enabled.

## State And Persistence
Persistent state is backend-provided dbwrap storage. Record values are null-terminated strings. HWM records are uint32. The code enforces id range filters on lookup and HWM high bounds on allocation.

## Dependencies And Integration
It depends on dbwrap, TDB string helpers, `idmap_rw_new_mapping`, SID helpers, and backend-specific context initialization by `idmap_tdb.c`, `idmap_tdb2.c`, and autorid code.

## Risks And Test Signals
Test allocation boundaries, invalid ID types, non-default allocation refusal, null map/SID, duplicate SID collisions, reverse insert failure cleanup, invalid/non-null-terminated DB values, malformed `UID`/`GID` records, range filters, `ID_REQUIRE_TYPE`, and writable versus read-only behavior. The allocation sequence can consume an HWM value before later storage fails; callers rely on transaction wrapping where available.
