# sources/test-tools/syzkaller/syz-cluster/pkg/blob/storage_test.go

## Purpose
LocalStorage contract test.

## Important APIs, Types, and Functions
TestLocalStorage.

## Control Flow
Writes two objects, reads them back, and checks bad URI/error cases.

## State and Persistence
Uses t.TempDir only.

## Dependencies and Integration Points
Integrated by app environment and services that offload logs, configs, patches, reports, and reproducers.

## Risks and Edge Cases
Risks include orphaned blobs after DB failures, URI validation gaps, upload close errors, and in-memory/local overwrite behavior.

## Test Signals
Covered by LocalStorage unit tests and higher-level service/controller tests.
