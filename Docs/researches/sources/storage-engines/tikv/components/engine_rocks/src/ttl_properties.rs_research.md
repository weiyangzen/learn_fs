<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/ttl_properties.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/ttl_properties.rs

## Purpose
`ttl_properties.rs` collects and decodes per-SST TTL expiration metadata for RawKV data in the default CF. It records minimum and maximum expiration timestamps in RocksDB user-collected properties.

## Important APIs, Types, and Functions
`RocksTtlProperties` encodes/decodes `engine_traits::TtlProperties` using `tikv.max_expire_ts` and `tikv.min_expire_ts`. `TtlPropertiesExt for RocksEngine::get_range_ttl_properties_cf` reads table properties over a key range and returns file-name/property pairs when TTL metadata exists.

`TtlPropertiesCollector<F: KvFormat>` is a RocksDB `TablePropertiesCollector`. It inspects only `DBEntryType::Put`, only TiKV data keys, and only raw key mode for the selected API format. `TtlPropertiesCollectorFactory<F>` creates collectors.

## Control Flow
During SST creation, `add` filters out non-put records, non-data keys, and non-raw keys. It decodes a raw value via `F::decode_raw_value`; if an expiration timestamp exists, it updates min/max through `TtlProperties::add`. Decode failures are logged and do not abort collection. `finish` returns encoded user properties.

Range lookup fetches table properties for `[start_key, end_key)`, returns empty for no SSTs, decodes each file's TTL properties, and includes only non-empty properties.

## State and Persistence Behavior
TTL min/max values are persisted as user-collected properties in SST metadata. Runtime range queries are read-only. Collector state is per-SST build and reset through factory creation.

## Dependencies and Integration Points
It depends on `api_version::KvFormat`, raw value encoding, TiKV key prefixes, RocksDB table-property collector traits, and `decode_properties::DecodeProperties`. TTL compaction or scheduling code can use `TtlPropertiesExt` to decide whether ranges contain expiring data.

## Risks and Edge Cases
The collector is documented for default CF only; using it on other CFs can produce meaningless data. `DBEntryType::BlobIndex` is skipped because the collector cannot parse blob values. API-version differences matter: V1ttl treats `expire_ts=0` as no TTL, while API V2 can record zero. Decode errors are logged but only cause missing TTL data, not write failure.

## Test Signals
Tests cover API V1ttl and V2 collection, non-put filtering, empty cases, min/max encoding, and codec round trips. Useful additions include blob-index records, non-data keys, decode errors, and range retrieval across multiple SSTs.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/ttl_properties.rs -->
