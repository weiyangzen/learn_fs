# sources/sync-backup/syncthing/internal/gen/discosrv/discosrv.pb.go

Purpose: Generated protobuf bindings for discovery server database and replication records.

Important APIs/types/functions: `DatabaseRecord` stores announced `DatabaseAddress` entries plus a `Seen` unix-nanos timestamp. `ReplicationRecord` adds the raw 32-byte device ID `Key` for replication transport. `DatabaseAddress` stores an address string and unix-nanos expiry. Generated reset, reflection, descriptor, and getter methods are present for all messages.

Control flow: `init` builds a descriptor with three messages and dependency indexes linking address lists to `DatabaseAddress`. The raw descriptor is lazily gzipped under `sync.Once`.

State and persistence behavior: These messages represent durable discovery-server state and replication payloads. Timestamp fields use nanoseconds, so callers must keep units consistent when pruning or comparing records.

Dependencies and integration points: Uses only the protobuf runtime. It integrates with discovery server storage/replication code that stores device addresses and distributes address updates between discovery nodes.

Risks: Address expiry and seen timestamps are plain `int64` values without validation here. Schema changes may break persisted discovery server data or replication compatibility.

Test signals: No direct test in the generated file; validated by discovery server storage and replication tests elsewhere.
