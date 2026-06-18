# Research: sources/sync-backup/syncthing/proto/dbproto/structs.proto

## sources/sync-backup/syncthing/proto/dbproto/structs.proto

Purpose: defines protobuf records persisted in Syncthing's database layer.

Important APIs/types: imports `bep/bep.proto` and `google/protobuf/timestamp.proto`; defines `FileInfoTruncated`, `FileVersion`, `VersionList`, `BlockList`, `IndirectionHashesOnly`, `Counts`, `CountsSet`, `ObservedFolder`, and `ObservedDevice`.

Control flow: schema-only. Database code serializes/deserializes these messages for file metadata, version lists, block lists, folder/device observation, and count buckets.

State and persistence: persistence is central here. `FileInfoTruncated` mirrors BEP `FileInfo` without blocks while preserving field numbers; `Counts` stores file/directory/symlink/deleted/bytes/sequence counters per folder/device or global state; observed records include timestamps and labels.

Dependencies and integration: tightly coupled to BEP schema and database migration compatibility. Risks include field-number mismatches with `bep.FileInfo`, losing host-local fields, and changing timestamp or sequence semantics. Test signals are database upgrade/load tests and generated-code compilation.
