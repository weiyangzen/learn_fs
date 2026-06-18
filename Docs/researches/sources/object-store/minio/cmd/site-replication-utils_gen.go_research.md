# sources/object-store/minio/cmd/site-replication-utils_gen.go

## Purpose
Generated tinylib/msgp serialization code for `SiteResyncStatus`, the persisted and transported site-replication resync status DTO from `site-replication-utils.go`.

## Important APIs, Types, And Functions
Implements `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` on `*SiteResyncStatus`. The encoded map uses compact msg field names from struct tags: `v` for version, `ss` for status, `did` for deployment ID, `bkts` for bucket statuses, `tb` for total buckets, and `cst` for embedded current target resync status.

## Control Flow
Decode and unmarshal read a map header, switch on field keys, decode known fields, allocate or clear `BucketStatuses`, and skip unknown fields. Encode and marshal write a fixed six-field map and delegate nested encoding to `ResyncStatusType` and `TargetReplicationResyncStatus`. `Msgsize()` estimates the encoded size including dynamic string/map entries.

## State And Persistence
No direct I/O occurs here. The generated methods define the binary representation used by site-resync metadata persistence and any msgp transport path. Deserialization mutates receiver state and clears existing bucket-status maps before loading new values.

## Dependencies And Integration Points
Depends on `github.com/tinylib/msgp/msgp` and msgp methods on nested resync status types. It is regenerated from `//go:generate msgp -file=$GOFILE` in `site-replication-utils.go` and supports `loadSiteResyncMetadata()`/`saveSiteResyncMetadata()` integration.

## Risks And Edge Cases
Manual edits would be overwritten and may diverge from struct tags. Field-name/tag changes are persistence-format changes. Unknown fields are skipped, which helps forward compatibility, but missing known fields leave zero values. Map iteration order for bucket statuses is nondeterministic in bytes.

## Test Signals
`site-replication-utils_gen_test.go` validates zero-value marshal/unmarshal, skip, encode/decode, size warning, and benchmarks for `SiteResyncStatus`.
