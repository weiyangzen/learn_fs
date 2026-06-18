# sources/sync-backup/syncthing/internal/gen/discoproto/local.pb.go

Purpose: Generated protobuf bindings for local discovery announce packets.

Important APIs/types/functions: Defines the `Announce` message with `Id []byte`, repeated `Addresses []string`, and `InstanceId int64`. Generated methods provide reflection, stringification, reset, descriptor access, and nil-safe getters.

Control flow: Runtime initialization builds one message descriptor from the raw `discoproto/local.proto` descriptor. Descriptor gzip compression is lazy and protected by `sync.Once`.

State and persistence behavior: The file does not persist state itself. It defines the serialized shape for local discovery announcements, so field numbers and types are network compatibility contracts. `InstanceId` helps distinguish process instances advertising the same device identity.

Dependencies and integration points: Uses the Go protobuf runtime. Integrated by discovery/beacon code that marshals local announcements and decodes inbound announcements.

Risks: Generated code should not be edited directly. Compatibility risk lies in altering the `.proto` schema without considering older nodes that expect these fields.

Test signals: No direct test in this file; exercised indirectly by local discovery tests and runtime interoperability.
