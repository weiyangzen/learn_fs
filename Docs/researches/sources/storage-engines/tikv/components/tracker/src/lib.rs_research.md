# sources/storage-engines/tikv/components/tracker/src/lib.rs

Purpose: request tracker model and response-detail writers for TiKV request timing, RocksDB scan stats, write pipeline timing, and RU v2 accounting.

Important APIs/types/functions: `Tracker`, `RequestInfo`, `RequestType`, `RequestMetrics`, `merge_time_detail`, `write_scan_detail`, `write_write_detail`, and `write_ru_v2`.

Control flow: request code creates `RequestInfo` from `kvrpcpb::Context`, mutates metrics through TLS/slab access, then writes metrics into protobuf details. Some scan MVCC fields are filled only when currently unset to avoid clobbering coprocessor-provided stats.

State and persistence: per-request in-memory metrics; protobuf detail messages carry the final serialized results to clients/telemetry.

Dependencies/integration: re-exports future tracking, TLS helpers, and global tracker slab; integrates with `kvproto::kvrpcpb`.

Risks: several write-detail fields subtract related timestamps and can underflow if metrics are recorded out of order; metrics are public fields, so invariants are convention-based.

Test signals: unit tests cover MVCC scan stat idempotence and non-overwrite behavior.
