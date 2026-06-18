# sources/user-network-fs/samba/source3/winbindd/idmap_tdb_common.h

## Purpose
This header defines the context contract and function prototypes for TDB-style idmap backends that reuse common allocation and lookup code.

## Important APIs, Types, And Functions
`struct idmap_tdb_common_context` contains a `db_context`, `idmap_rw_ops`, `max_id`, UID/GID HWM key strings, optional single-lookup function hooks, and backend `private_data`. It declares all common allocation, storage, and lookup functions implemented in `idmap_tdb_common.c`.

## Control Flow
No executable flow exists here. The comments define how backends install the context in `idmap_domain->private_data`, when hooks are used, and what record shapes are stored.

## State And Persistence
The context points to persistent dbwrap storage and names the HWM records. `private_data` lets backends attach script/config state while still using common logic.

## Dependencies And Integration
It includes `idmap.h` and `dbwrap/dbwrap.h`. Backends must initialize the db pointer, HWM keys, max ID, and RW callbacks before invoking common functions.

## Risks And Test Signals
Build tests should catch mismatched hook signatures. Backend tests should verify each context is fully initialized, especially `rw_ops`, HWM keys, and `max_id`; null fields lead to aborts or invalid db operations.
