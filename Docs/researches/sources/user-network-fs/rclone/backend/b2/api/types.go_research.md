# Research: sources/user-network-fs/rclone/backend/b2/api/types.go

## Purpose
This file defines Go representations of Backblaze B2 API request and response payloads plus small helpers for B2 error fatality, millisecond timestamps, and versioned filenames. It is a schema and utility layer consumed by higher-level B2 backend code.

## Important APIs, Types, and Functions
- `Error` models B2 JSON error responses, implements `error`, and marks HTTP 403 as fatal via `Fatal`.
- `Bucket`, `LifecycleRule`, and `ServerSideEncryption` model bucket configuration and encryption settings.
- `Timestamp` wraps `time.Time` with B2's millisecond-since-epoch JSON encoding and filename version helpers.
- `HasVersion`, `Timestamp.AddVersion`, and `RemoveVersion` delegate version parsing/formatting to `lib/version`.
- `File` and `FileInfo` model listed and uploaded file versions.
- `StorageAPI` and `AuthorizeAccountResponse` represent authorization discovery, allowed capabilities, upload/download API URLs, and part-size recommendations.
- Request/response structs cover bucket listing, file listing, upload URL, download authorization, bucket creation/update/delete, file delete/hide/info, large file start/upload part/finish/cancel, file copy, and part copy.

## Control Flow
Most types are passive JSON schemas. `Timestamp.MarshalJSON` converts UTC nanoseconds to integer milliseconds and writes a JSON number. `UnmarshalJSON` parses a JSON number into seconds plus nanosecond remainder and forces UTC. `Equal` returns false if either side is zero before calling `time.Equal`. Version helpers only wrap shared filename-version utilities. `Error.Fatal` makes retry policy callers treat 403 authorization failures as non-retryable.

## State and Persistence Behavior
The file has no persistence side effects. It defines in-memory structs that serialize to and from B2 API JSON. Timestamp conversion truncates sub-millisecond precision during marshaling, matching B2's contract.

## Dependencies and Integration Points
It depends on rclone `fserrors.Fataler` for fatal retry classification and `lib/version` for timestamp-in-filename behavior. Higher-level B2 API client code relies on the JSON tags matching B2 endpoints, especially optional fields for lifecycle rules, encryption, metadata directives, destination buckets, and large file operations.

## Risks and Edge Cases
- `Timestamp.MarshalJSON` has a pointer receiver; callers with non-addressable values may rely on encoding/json addressability behavior.
- Timestamp marshaling truncates nanoseconds to milliseconds, so round trips lose sub-millisecond precision.
- `Timestamp.Equal` deliberately returns false for two zero timestamps, which is nonstandard and must be understood by callers.
- `StorageAPI.Allowed.NamePrefix` is `any`, reflecting flexible/null API values but pushing type handling to callers.
- Struct comments include one stale copy/paste note: `DeleteBucketRequest` says "used to create a bucket".
- Schema drift in B2 API fields would not be caught without integration tests or JSON fixture tests.

## Test Signals
`types_test.go` tests timestamp marshal/unmarshal, zero detection, and `Equal` semantics. There are no tests in this group for request/response JSON field coverage, fatal error classification, version filename helpers, or encryption/copy schemas.
