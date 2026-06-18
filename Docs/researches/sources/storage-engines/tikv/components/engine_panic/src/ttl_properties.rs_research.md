# sources/storage-engines/tikv/components/engine_panic/src/ttl_properties.rs

Purpose: Panic skeleton for TTL range property access.

Important APIs and types: `PanicEngine` implements `TtlPropertiesExt::get_range_ttl_properties_cf`.

Control flow and state: The method panics and stores no TTL metadata.

Dependencies and integration: Real engines use this for TTL-aware range scans or compaction decisions.

Risks: Runtime use panics.

Test signals: No tests.
