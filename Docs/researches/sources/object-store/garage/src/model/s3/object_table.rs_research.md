# sources/object-store/garage/src/model/s3/object_table.rs

## Purpose
This file defines the primary S3 object metadata table. It stores object keys, version history, upload state, delete markers, inline/first-block data pointers, object metadata, encryption metadata, checksums, and hooks that cascade cleanup to version and multipart tables.

## Important APIs, types, and functions
`Object` is keyed by bucket UUID and object key and contains sorted `ObjectVersion` entries. `ObjectVersion` has UUID, timestamp, and `ObjectVersionState`: `Uploading`, `Complete`, or `Aborted`. `ObjectVersionData` is `DeleteMarker`, `Inline(meta, bytes)`, or `FirstBlock(meta, hash)`. `ObjectVersionMeta`, `ObjectVersionEncryption`, `ObjectVersionMetaInner`, `ChecksumAlgorithm`, `ChecksumValue`, and `ChecksumType` model headers, SSE-C encrypted metadata, compression flags, ETags, sizes, and checksum semantics. `Object::new`, `add_version`, `versions`, `ObjectVersion::is_uploading`, `is_complete`, `is_data`, `ChecksumValue::algorithm`, CRDT merges, `ObjectTable::updated`, filters, and `CountedItem` are central.

## Control flow
Constructing an object inserts versions sorted by `(timestamp, uuid)`. Merging adds or merges same-key versions, then discards obsolete earlier versions before the latest complete version. State merge makes `Aborted` dominant over local state, `Complete` replace `Uploading`, and complete data merge via `AutoCrdt`. Table updates first update object counters. Then, for old versions absent from the new object or newly aborted, they queue deleted `Version` rows. For old multipart uploading versions that disappear or stop uploading, they queue deleted `MultipartUpload` rows.

## State and persistence behavior
The file contains migrations from v08 to v09, v010, and v2. v09 adds multipart upload flags; v010 introduces encryption metadata and checksum values; v2 adds checksum type. Current object table name is `object`. Tombstone status is only a single delete-marker version. Counters aggregate live object count, unfinished upload count, and bytes by bucket.

## Dependencies and integration points
It depends on Garage DB, table CRDTs, sharded replication, index counters, MPU table, and version table. S3 PUT/GET/DELETE/list/multipart/lifecycle code consumes and mutates this model; version table and block ref table handle data block cleanup.

## Risks and edge cases
Obsolete-version pruning after merge means historical versions before the latest complete state are intentionally removed, so versioning semantics are simplified compared with full S3 version history. Hook failures log and continue, leaving cleanup for repair. Encryption metadata may be encrypted, so callers must handle plaintext vs SSE-C branches. Inline encrypted data is never compressed while block data may be compressed/encrypted depending on flags. The tombstone definition only matches one delete marker; multiple versions with a latest delete marker are not table tombstones.

## Test signals
No direct unit tests in this file, but S3 integration tests cover many paths. Focused tests should cover migrations, version ordering/pruning, state merge precedence, counter metrics, delete cascades to version/MPU tables, checksum type migration, and encrypted metadata handling.
