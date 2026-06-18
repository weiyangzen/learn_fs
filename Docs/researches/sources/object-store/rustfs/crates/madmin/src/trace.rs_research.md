# sources/object-store/rustfs/crates/madmin/src/trace.rs

Purpose: defines trace type bitmasks and trace-event payload schemas for admin/service tracing.

Important APIs/types/functions: `TraceType(u64)` exposes constants for OS, storage, S3, internal, scanner, decommission, healing, batch jobs, rebalance, replication resync, bootstrap, FTP, ILM, and `ALL`. Methods `new`, `contains`, `overlaps`, `single_type`, `merge`, `set_if`, and `mask` implement bitmask operations. `TraceInfo` is the current event payload; `TraceInfoLegacy` wraps request/response/stats/storage/OS legacy shapes. Supporting structs include `TraceHTTPStats`, `TraceCallStats`, `TraceRequestInfo`, `TraceResponseInfo`, `StorageStats`, and `OSStats`.

Control flow: bitmask methods are simple bitwise checks/mutations. Payload structs rely on serde renames and optional omissions. `TraceInfo::mask` converts stored numeric type back into `TraceType`.

State and persistence: no persistence. Trace records are transient serialized event snapshots with timing, path, bytes, messages, errors, custom key/value data, HTTP stats, and optional heal result.

Dependencies/integration: uses `chrono::DateTime<Utc>`, serde, `Duration`, `HashMap`, and `heal_commands::HealResultItem`. `service_commands.rs` builds `TraceType` masks from URI parameters.

Risks: many payload fields are private, preventing direct downstream construction and making serde the main access path. `Duration` serde compatibility must match trace consumers. `ALL` assumes metrics-all remains last; adding a new trace constant requires updating the mask width.

Test signals: no local tests. Bitmask operations and trace serde round trips are not directly covered in this module.
