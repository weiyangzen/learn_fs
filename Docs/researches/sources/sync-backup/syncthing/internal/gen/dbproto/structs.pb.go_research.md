# sources/sync-backup/syncthing/internal/gen/dbproto/structs.pb.go

Purpose: Generated Go protobuf bindings for `dbproto/structs.proto`, defining database persistence messages used by Syncthing's internal index and metadata database. It mirrors selected BEP protocol structures while omitting or separating heavy fields for storage efficiency.

Important APIs/types/functions: The exported message types are `FileInfoTruncated`, `FileVersion`, `VersionList`, `BlockList`, `IndirectionHashesOnly`, `Counts`, `CountsSet`, `ObservedFolder`, and `ObservedDevice`. Each has generated `Reset`, `String`, `ProtoReflect`, deprecated `Descriptor`, and nil-safe getters. `FileInfoTruncated` stores file metadata without inline blocks: name, size, type, permissions, modified time split into seconds/nanos, modified-by, version vector, sequence, symlink target, block hashes, encryption metadata, platform data, deletion/invalid/no-permission flags, and host-local implementation fields such as local flags, version hash, and encryption trailer size. `BlockList` carries the omitted BEP block list separately. `Counts` and `CountsSet` persist summary counts and creation timestamps. `ObservedFolder` and `ObservedDevice` persist remote observation metadata.

Control flow: There is no domain logic beyond generated protobuf runtime behavior. `init` calls `file_dbproto_structs_proto_init`, which builds a `protoreflect.FileDescriptor` through `protoimpl.TypeBuilder`, wires BEP and timestamp dependencies, and nils raw descriptor/type slices after initialization. Raw descriptor compression is guarded by `sync.Once`.

State and persistence behavior: These message structs are persistence contracts. Field numbers, names, and protobuf wire types are the durable database schema, including high-numbered local fields. Changing or removing fields risks breaking database compatibility and migrations. Nil getters intentionally return zero values for partially decoded or absent data.

Dependencies and integration points: Depends on generated `internal/gen/bep` types (`Vector`, `FileInfoType`, `PlatformData`, `BlockInfo`) and `google.protobuf.Timestamp`. Consumers are expected to marshal/unmarshal through `google.golang.org/protobuf/proto` in Syncthing database code.

Risks: Because this is generated code, manual edits will be overwritten and may diverge from the `.proto` source. The most sensitive risks are schema drift, accidental reuse of removed field numbers, and confusing host-local fields with protocol wire fields. No validation is performed by the generated accessors; callers must enforce semantic constraints.

Test signals: No direct tests in this file. Coverage comes indirectly from database/index serialization tests and any tests that round-trip file metadata, counts, observed folders/devices, or block indirection through the database.
