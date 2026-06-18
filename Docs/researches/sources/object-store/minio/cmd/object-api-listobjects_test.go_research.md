# sources/object-store/minio/cmd/object-api-listobjects_test.go

## Purpose
This file provides broad regression coverage for object listing behavior: classic `ListObjects`, versioned listing, continuation behavior, versioned delete-marker handling, listing under lifecycle expiration, and a benchmark for large listings.

## Important APIs, types, and functions
Entry points include `TestListObjectsVersionedFolders`, `TestListObjectsOnVersionedBuckets`, `TestListObjects`, `TestDeleteObjectVersionMarker`, `TestListObjectVersions`, `TestListObjectsContinuation`, `BenchmarkListObjects`, and `TestListObjectsWithILM`. Core object-layer APIs exercised are `MakeBucket`, `PutObject`, `DeleteObject`, `ListObjects`, `ListObjectVersions`, and `ListObjectsV2`. Helpers include `objInfoNames`, `initFSObjectsB`, lifecycle parsing, bucket metadata updates, and global expiry state setup.

## Control flow
The tests create buckets with and without versioning, upload deterministic object sets, and compare listing results against table-driven `ListObjectsInfo` or `ListObjectVersionsInfo` expectations. The non-versioned and versioned listing tests share much of the same object corpus and cover invalid bucket names, missing buckets, empty buckets, negative/zero/large `maxKeys`, truncation, `NextMarker`, markers before and after result ranges, prefix filtering, delimiter grouping, custom delimiters, trailing slash object lookups, empty directory markers, and prefix matches around `xl.meta`-like paths.

`testListObjectsVersionedFolders` specifically checks that delete markers on directory objects are represented correctly in versioned listings and hidden or exposed appropriately in normal listings. `testDeleteObjectVersion` modifies bucket metadata to suspend versioning, then verifies delete behavior with and without the null version ID. `testListObjectsContinuation` pages through results using `NextMarker`, including a branch that deliberately resumes from the last object name rather than the returned marker to guard continuation robustness. `testListObjectsWithILM` installs a lifecycle expiration rule and verifies `ListObjectsV2` does not expose expired objects while still paginating without infinite loops.

## State and persistence behavior
These tests exercise persisted object namespace state, bucket versioning metadata, delete markers, lifecycle metadata, global metadata system updates, and global expiry state. They rely on lexicographic ordering and stable directory-prefix projection from the backend. The ILM test uses older modification times to make some persisted objects logically expired even though they were just written by the test.

## Dependencies and integration points
Dependencies include the object-layer test harness, MD5/hex helpers, lifecycle parsing, global bucket metadata and notification systems, global versioning and expiry systems, and benchmark initialization through `initObjectLayer`, `newTestConfig`, and `initAllSubsystems`. The file integrates listing behavior with delete, versioning, lifecycle, and metadata subsystems.

## Risks and test signals
This file is a major regression signal for S3-compatible listing semantics. It can catch off-by-one marker handling, wrong truncation state, missing `NextMarker`, incorrect prefix grouping, directory-marker visibility bugs, version/delete-marker ordering regressions, lifecycle filtering loops, and max-keys normalization errors. Gaps include ListObjectsV2 continuation-token semantics beyond ILM, owner/fetch-owner fields, encoding type, and detailed version ID marker assertions.
