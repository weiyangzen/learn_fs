# sources/object-store/daos/src/vos/ilog.h

## Purpose
Public interface for VOS incarnation logs. It exposes the durable root placeholder, log entry identity/status types, callback contract for DTX integration, fetch result containers, iteration macros, mutation APIs, aggregation API, timestamp-index access, version access, and validation helpers.

## Important APIs, Types, And Functions
`struct ilog_id` packs DTX id, punch/update minor epochs, and major epoch. `struct ilog_df` is an opaque 24-byte durable root. `enum ilog_status` describes invalid, committed, uncommitted, and removed states. `struct ilog_desc_cbs` bridges to transaction status/add/delete logic. `struct ilog_entry`, `struct ilog_info`, and `struct ilog_entries` model fetched logs. APIs cover lifecycle (`ilog_init/create/open/close/destroy`), mutation (`ilog_update`, `ilog_set_flags`, `ilog_persist`, `ilog_abort`), aggregation/fetch, and validation.

## Control Flow
Callers create a root in persistent memory, open it with callbacks and fixed-epoch mode, update/punch with epoch range and minor epoch, persist/abort DTX-backed entries, fetch entries for visibility checks, aggregate stale ranges, then close/destroy. Fetch callers use `ilog_fetch_init`, optional `ilog_fetch_move`, iteration macros, and `ilog_fetch_finish`.

## State And Persistence
The header intentionally hides the real root layout behind `ilog_df`; `ilog_internal.h` defines the inline/array layout. `ILOG_PRIV_SIZE` reserves private cache space inside `ilog_entries`, so callers allocate one structure while implementation stores embedded cache state.

## Dependencies And Integration
Depends only on DAOS public types and an opaque `umem_instance`; implementation links to VOS/DTX. Used by `vos_ilog.h` wrappers and VOS object/key trees.

## Risks
The API requires nonzero epochs/minor epochs for meaningful updates. Callback omissions default some behavior to committed/no-op, useful for tests but risky if a production caller forgets DTX hooks. Iteration macros assume `ilog_fetch_init` has set up internal storage. Comments contain typos and one duplicated parameter name, but API intent is clear.

## Test Signals
Tests should validate lifecycle error returns, callback ordering, iteration forward/reverse behavior, cache move/finalization, aggregation return value `1` for empty logs, and validation/corruption helpers.
