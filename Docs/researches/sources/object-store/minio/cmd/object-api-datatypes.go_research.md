# sources/object-store/minio/cmd/object-api-datatypes.go

This file defines many core object API data contracts: backend type aliases, object-size and version-count histogram intervals, bucket metadata, object metadata, replication payloads, multipart/listing responses, transition/delete records, completed multipart request structures, and get-object-attributes XML responses.

Key APIs and methods include `ObjectInfo.ExpiresStr`, `ObjectInfo.ArchiveInfo`, `ObjectInfo.Clone`, `ObjectInfo.tierStats`, `ReplicateObjectInfo.ToObjectInfo`, and `ListMultipartsInfo.Lookup`. `ObjectInfo` is the central structure and carries bucket/name, modtime, size, actual size, directory marker, ETag, version status, delete marker, transition/restore state, content headers, storage class, replication and purge status, user metadata/tags, parts, internal reader/writer handles excluded from msgp/json, access time, legacy/inlined flags, checksums, and data/parity counts. `Clone` deep-copies `UserDefined` but carries slices and readers by reference. `ArchiveInfo` decrypts archive metadata when marked encrypted.

State is structural and serialized by generated msgp code in `object-api-datatypes_gen.go`. These types are passed across object-layer, replication, listing, multipart, lifecycle, transition, and admin paths. Histogram interval globals feed data usage accounting and metrics.

Risks: schema changes affect on-disk or RPC msgp compatibility and require regeneration. `ToObjectInfo` is explicitly partial and sets `DeleteMarker: true`, so callers must not treat it as complete metadata. `Clone` is not a full deep copy for all nested fields. There are no direct tests in this file; generated serialization and higher-level object API tests provide coverage.
