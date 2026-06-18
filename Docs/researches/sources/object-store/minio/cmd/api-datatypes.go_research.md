# sources/object-store/minio/cmd/api-datatypes.go

## Purpose
`api-datatypes.go` defines small XML-facing datatypes used by S3-compatible API request and response processing, especially multi-object delete and create-bucket location parsing. The types bridge MinIO internal replication/versioning metadata with AWS-compatible XML field names.

## Important APIs, Types, And Functions
- `DeletedObject` describes a deleted object in XML responses with optional delete-marker fields, object key, version ID, delete-marker modification time, replication state, and an internal `found` flag.
- `DeleteMarkerMTime` embeds `time.Time` and customizes XML marshaling.
- `DeleteMarkerMTime.MarshalXML` omits zero timestamps and emits RFC3339 timestamps otherwise.
- `ObjectV` carries an object key and version ID.
- `ObjectToDelete` embeds `ObjectV` and adds delete-marker replication status, version purge status, internal purge-status aggregation, and replication decision text.
- `createBucketLocationConfiguration` maps the `CreateBucketConfiguration` XML body and location constraint.
- `DeleteObjectsRequest` maps the multi-delete request body with quiet mode and a list of `ObjectToDelete` entries.

## Control Flow
There is no runtime control flow beyond XML marshaling. The Go `encoding/xml` package uses field tags during request decode and response encode. `DeleteMarkerMTime.MarshalXML` checks `IsZero`; when zero it returns nil without emitting an element, otherwise it encodes the embedded time formatted with `time.RFC3339`.

## State And Persistence Behavior
The file defines transient request/response structs only. It does not persist state. Internal fields such as `ReplicationState`, `ReplicateDecisionStr`, and `found` are used by other API logic to carry decisions alongside XML-facing data without exposing them directly.

## Dependencies And Integration Points
The file depends on `encoding/xml` and `time`, plus package-local types `ReplicationState` and `VersionPurgeStatusType`. It integrates with S3 API handlers that parse `CreateBucketConfiguration` and `DeleteObjectsRequest` XML bodies and produce `DeletedObject` response entries. Replication and versioning subsystems consume the hidden status fields.

## Risks And Edge Cases
XML tag compatibility is important because clients expect AWS S3 field names such as `DeleteMarkerVersionId`, `Key`, `VersionId`, `CreateBucketConfiguration`, and `LocationConstraint`. A zero `DeleteMarkerMTime` emits no XML, which is intentional but can surprise callers expecting an empty element. The unexported `found` flag is not serialized and must only be interpreted inside package logic. This file does not validate object names, versions, or replication status values; validation must happen in consuming handlers.

## Test Signals
No tests in this subset directly cover these datatypes. Coverage likely comes from broader S3 API delete/create-bucket tests outside the listed files. Relevant missing tests would include XML round trips for multi-delete quiet/object entries and `DeleteMarkerMTime` zero/non-zero marshal behavior.
