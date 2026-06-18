# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Audit.h

Purpose: defines audit phases, audit types, and serialized request/state structures for storage and metadata validation workflows.

Important APIs and types: `AuditPhase` covers invalid/running/complete/error/failed. `AuditType` covers HA, replica, location metadata, storage-server shard, restore, and metadata encoding validation. `AuditStorageState` persists audit id, DD id, audit server id, range, type, phase, engine type, and error. `AuditStorageRequest` and `TriggerAuditRequest` are RPC/request structures with reply promises.

State and persistence: `AuditStorageState` is a persisted contract with `file_identifier` and serializer field order. `ddId` coordinates ownership across data distributor changes; phase/error encode progress and failure.

Dependencies and integration: includes `FDBTypes.h` and `fdbrpc.h`; used by data distributor, storage server audit actors, and management APIs that trigger/cancel audits.

Risks: `setType` and `setPhase` store enum values as `uint8_t`; invalid values can be represented if deserialized from corrupt data. The `setType` implementation in request/trigger forms assigns from `this->type` instead of the argument, which is suspicious and worth review if those setters are used.

Test signals: audit management and simulation tests should cover trigger, resume, phase transition, and cancellation serialization.
