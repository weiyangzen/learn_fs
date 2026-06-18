<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/pb/badgerpb4.proto -->
# sources/storage-engines/badger/pb/badgerpb4.proto

## Purpose
This file is the source protobuf schema for Badger v4 internal and external wire messages.

## Important APIs, Types, And Functions
Messages: `KV`, `KVList`, `ManifestChangeSet`, `ManifestChange`, `Checksum`, `DataKey`, and `Match`. Enums: `EncryptionAlgo`, nested `ManifestChange.Operation`, and nested `Checksum.Algorithm`. The `go_package` is `github.com/dgraph-io/badger/v4/pb`.

## Control Flow
There is no runtime control flow. `protoc` plus `protoc-gen-go` consumes this schema to generate `badgerpb4.pb.go`.

## State And Persistence Behavior
`ManifestChangeSet` atomically groups table creates/deletes for the manifest. `ManifestChange` stores table ID, operation, level, encryption key ID, encryption algorithm, and compression. `KV`/`KVList` represent key/value data, stream IDs, stream completion, and allocation refs. `DataKey` stores encryption key metadata. `Match` stores subscription prefix filters and ignored byte ranges.

## Dependencies And Integration Points
The schema drives generated Go code used by manifest persistence, subscriptions/publisher, streams, key registry, and checksum code. `pb/gen.sh` regenerates bindings.

## Risks And Edge Cases
Field numbers are durable API. Renaming is less dangerous than renumbering, but removing/reusing fields or changing enum numbers would break existing manifests, streams, or key registry data. `EncryptionAlgo` currently contains only AES, so adding algorithms requires implementation support beyond the schema.

## Test Signals
`pb/protos_test.go` verifies generated Go stays in sync with this schema.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/pb/badgerpb4.proto -->
