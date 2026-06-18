# sources/storage-engines/tikv/components/engine_tirocks/src/properties/ttl.rs

Purpose: Collects and queries raw-key TTL expiration bounds from TiRocks SST user properties for default-CF RawKV data.

Important APIs and control flow: `encode_ttl` and `decode_ttl` store `tikv.max_expire_ts` and `tikv.min_expire_ts`. `TtlPropertiesExt for RocksEngine` scans table properties in a range, decodes TTL properties, and returns file-name/property pairs while skipping tables without TTL metadata. `TtlPropertiesCollector<F>` filters for put entries, TiKV data-key prefix, and raw key mode, decodes `RawValue`, and updates min/max expiration timestamps before finish writes properties if any TTL was seen.

State, persistence, and dependencies: TTL bounds are persisted in SST user properties and depend on `api_version::KvFormat`, `keys::DATA_PREFIX_KEY`, TiRocks table-property collectors, and engine-trait TTL structures.

Integration points, risks, and test signals: Used by RawKV TTL scans and GC/compaction estimation. Risks include decode failures being logged but ignored, only default-CF validity, missing TTL properties on preexisting SSTs, UTF-8 assumptions for file names, and source-version skew: this adapter uses zero as the empty sentinel while the adjacent trait file defines optional TTL bounds. Tests cover API V1ttl/API V2 encoding behavior, min/max handling, non-put exclusion, and empty/no-TTL error paths.
