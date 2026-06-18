# sources/storage-engines/tikv/components/engine_traits/src/ttl_properties.rs

Purpose: Defines TTL property aggregation and range query APIs.

Important APIs and control flow: `TtlProperties` stores optional maximum and minimum expiration timestamps. `add` merges a single timestamp, `merge` updates optional extrema, and `is_some`/`is_none` report whether any TTL bound exists. `TtlPropertiesExt::get_range_ttl_properties_cf` returns per-file TTL properties for a CF and key range.

State, persistence, and dependencies: The struct is transient aggregation state, usually decoded from persisted SST properties by implementors.

Integration points, risks, and test signals: Used by RawKV TTL and MVCC property aggregation. Risks include option-vs-zero sentinel mismatches with older adapters, merging none/some incorrectly, and per-file aggregation leaving final range interpretation to callers. Unit tests cover add, merge, none/some behavior, and timestamp zero handling.
