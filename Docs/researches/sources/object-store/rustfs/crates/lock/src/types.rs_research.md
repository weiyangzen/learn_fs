<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/types.rs -->
# sources/object-store/rustfs/crates/lock/src/types.rs

Purpose: `types.rs` defines the crate-level lock protocol model used by distributed locks, clients, namespace APIs, health reporting, and wait/deadlock metadata. It is distinct from `fast_lock/types.rs` and is the serialization-facing model for many client paths.

Important APIs/types/functions: lock enums include `LockType`, `LockStatus`, and `LockPriority`. `LockInfo` stores id, resource, type, status, owner, acquired/expires/refresh times, metadata, priority, and optional wait start. `LockId` combines `ObjectKey` with a UUID and has `new`, `new_unique`, `as_str`, default, display, and serde. `LockMetadata` supports builder methods for client info, operation id, priority, and tags. `LockRequest` stores lock id/resource/type/owner/acquire timeout/TTL/metadata/priority/deadlock flag/log suppression and has builder methods. `LockResponse` models success/failure/waiting responses. `LockStats`, `NodeInfo`, `ClusterInfo`, `HealthInfo`, timestamp helpers, `DeadlockDetectionResult`, `WaitGraphNode`, and `WaitQueueItem` round out monitoring and deadlock/wait-queue structures.

Control flow: most methods are builders or inspectors. `LockInfo` checks expiry/remaining validity against `SystemTime::now`. `LockRequest::new` generates a unique lock id and default 10-second acquire timeout/30-second TTL. `LockResponse` constructors encode success/failure/waiting variants. Timestamp helpers convert between UNIX seconds and `SystemTime`.

State and persistence behavior: all structs are serde-compatible and suitable for RPC/admin payloads. UUIDs are generated per request/id; timestamps use `SystemTime`. No storage is performed here, but these types define what can be serialized over local/remote lock clients.

Dependencies and integration points: depends on `serde`, `uuid`, and `ObjectKey` from the fast-lock public exports. Used by `client`, `distributed_lock`, `namespace`, `local_lock`, remote locker code, and storage error mapping. `local_lock.rs` maps this model to fast-lock requests.

Risks: there are duplicate priority and mode enums between this file and `fast_lock/types.rs`, requiring explicit mapping. `LockMetadata.priority` says lower number means higher priority, while `LockPriority` enum uses larger discriminants for higher priority; consumers must not conflate them. `LockInfo::has_expired` uses wall-clock time and can be affected by clock changes. `deadlock_detection` and wait-graph types are data-model hooks; actual detection behavior depends on other modules.

Test signals: direct tests are not in this file, but namespace and distributed-lock tests heavily exercise `LockRequest`, `LockResponse`, `LockId`, and `LockStats`. Serialization compatibility should be covered by RPC tests that round-trip these structures.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/lock/src/types.rs -->
