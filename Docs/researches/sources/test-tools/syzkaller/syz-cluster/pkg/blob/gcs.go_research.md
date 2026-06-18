# sources/test-tools/syzkaller/syz-cluster/pkg/blob/gcs.go

## Purpose
GCS-backed blob.Storage implementation.

## Important APIs, Types, and Functions
NewGCSClient, gcsDriver.Write, gcsDriver.Read, parseURI.

## Control Flow
Write copies a reader into gcs.Client.FileWriter under bucket/path parts; Read validates gcs://bucket/object URIs.

## State and Persistence
Persists blobs outside Spanner; services store returned URIs.

## Dependencies and Integration Points
Integrated by app environment and services that offload logs, configs, patches, reports, and reproducers.

## Risks and Edge Cases
Risks include orphaned blobs after DB failures, URI validation gaps, upload close errors, and in-memory/local overwrite behavior.

## Test Signals
Covered by LocalStorage unit tests and higher-level service/controller tests.
