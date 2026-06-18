# sources/object-store/rustfs/crates/madmin/src/info_commands.rs

Purpose: defines the Rust serializable data model behind admin info/status responses: disk inventory, backend topology, per-server properties, service health summaries, bucket/object usage counters, and the top-level `InfoMessage`. It is a wire-contract module, not an executor.

Important APIs/types/functions: `ItemState` maps `offline`, `initializing`, and `online` strings; constants mirror those values. `Disk`, `DiskMetrics`, and `HealingDisk` describe drive capacity, throughput, runtime state, inode counters, physical devices, and heal progress. `StorageInfo`, `BackendDisks`, `BackendInfo`, `BackendByte`, `BackendType`, `FSBackend`, and `ErasureBackend` represent FS/erasure layouts and parity/set counts. `ServerProperties`, `Services`, `Kms`, `Ldap`, `Status`, `Buckets`, `Objects`, `Versions`, `DeleteMarkers`, `Usage`, `ErasureSetInfo`, and `InfoMessage` model the admin response tree. `BackendDisks::sum` is the only aggregation helper.

Control flow: runtime logic is limited to enum/string conversion and simple summing. Most behavior is serde field mapping through `rename`, `default`, and `skip_serializing_if`; `InfoMessage` composes optional subsections for partial admin responses.

State and persistence: no persistence is performed. State is represented as deserialized snapshots from remote/admin APIs. Backward compatibility is explicit in optional disk fields such as `runtimeState`, capacity observation metadata, and `physicalDeviceIds`.

Dependencies/integration: depends on serde, `time::OffsetDateTime`, `SystemTime`, and `metrics::TimedAction`. It is publicly re-exported by `madmin::lib`, and consumed by admin clients and site replication/user types through `BackendInfo`.

Risks: the wire schema is sensitive to serde names, casing, and optional defaults. `ItemState::from_string` is case-sensitive. Several numeric values can be large but are plain `u64`/`usize`; callers must avoid interpreting missing optional fields as known zero values.

Test signals: extensive unit tests cover state conversion, defaults, value construction, serde round trips, msgpack legacy/forward compatibility for `Disk`, physical device serialization, backend sums, constants, debug formatting, and approximate memory sizing.
