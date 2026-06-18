# sources/storage-engines/tikv/components/cdc/src/txn_source.rs

## Purpose
`txn_source.rs` defines bit allocation helpers for `kv.TxnSource`, allowing CDC to detect writes originating from TiCDC, lossy DDL reorg backfill, and Lightning physical import mode.

## Important APIs, Types, and Functions
- `TxnSource(u64)` wraps the source bitmap.
- `is_cdc_write_source_set` tests the low 8 bits.
- `is_lossy_ddl_reorg_source_set` tests bits shifted by `LOSSY_DDL_REORG_SOURCE_SHIFT`.
- `is_lightning_physical_import` checks bit 16.
- Test-only setters/getters create bitmap cases without exposing mutation APIs in production.
- `From<TxnSource> for u64` exports the raw value.

## Control Flow
There is no runtime control loop. Callers pass a raw transaction source into static predicates, and each predicate masks or shifts the bitmap to determine whether a class of source metadata is present.

## State and Persistence Behavior
The bitmap is carried in transaction metadata outside this file. The wrapper itself is copyable and has no heap or persistent state. Bit layout is part of an external contract with TiDB/TiCDC/Lightning writers.

## Dependencies and Integration Points
This module is intentionally dependency-light. It integrates with CDC filtering logic that needs to skip or classify writes by source, and with transaction metadata producers that set `kv.TxnSource`.

## Risks and Edge Cases
Bit allocation is compatibility-sensitive. `is_lossy_ddl_reorg_source_set` checks all bits above the lossy shift rather than masking only the lossy 8-bit field, so Lightning/import bits also make it return true; this appears deliberate from current code but should be validated when adding upper-bit meanings.

## Test Signals
Unit tests cover setting/getting CDC bits, lossy DDL reorg bits, and Lightning import detection, including default false cases.
