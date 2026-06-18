# sources/test-tools/syzkaller/syz-cluster/pkg/blob/storage.go

## Purpose
Blob storage interface and local test implementation.

## Important APIs, Types, and Functions
Storage, LocalStorage, NewLocalStorage, Write, Read, ReadAllBytes.

## Control Flow
Local Write base64-encodes joined parts and writes a file; Read validates local:// and opens it.

## State and Persistence
Local filesystem persistence for tests; production uses other Storage implementations.

## Dependencies and Integration Points
Integrated by app environment and services that offload logs, configs, patches, reports, and reproducers.

## Risks and Edge Cases
Risks include orphaned blobs after DB failures, URI validation gaps, upload close errors, and in-memory/local overwrite behavior.

## Test Signals
Covered by LocalStorage unit tests and higher-level service/controller tests.
