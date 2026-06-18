# sources/storage-engines/tikv/components/engine_panic/src/mvcc_properties.rs

Purpose: Panic skeleton for MVCC table/range property access.

Important APIs and types: `PanicEngine` implements `MvccPropertiesExt::get_mvcc_properties_cf`, taking CF, safe point, and key range.

Control flow and state: The method panics and returns no properties.

Dependencies and integration: Uses `txn_types::TimeStamp` and `engine_traits::MvccProperties`. Real engines use this for split/check and GC-related range statistics.

Risks: Runtime use panics.

Test signals: No tests.
