# sources/storage-engines/tikv/components/hybrid_engine/src/db_vector.rs

Purpose: unifies values returned from disk snapshots and region-cache snapshots behind one `DbVector`.

Important APIs/types/functions: `HybridDbVector<EK, EC>`, `try_from_disk_snap`, `try_from_cache_snap`, `Deref<[u8]>`, `Debug`, and `PartialEq<&[u8]>`.

Control flow: caller-selected disk/cache snapshot lookup returns an optional engine-specific vector, wrapped as `Either::Left` or `Either::Right`; all byte access dispatches through that enum.

State and persistence: owns read result bytes; no mutation or persistence.

Dependencies/integration: used by `HybridEngineSnapshot`’s `Peekable` implementation; depends on `engine_traits` and `tikv_util::Either`.

Risks: wrapper behavior is only as stable as the underlying engine `DbVector`; equality impl is narrow.

Test signals: indirectly covered by hybrid snapshot point-read tests.
