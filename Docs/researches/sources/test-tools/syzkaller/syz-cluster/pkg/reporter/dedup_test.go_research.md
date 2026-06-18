# sources/test-tools/syzkaller/syz-cluster/pkg/reporter/dedup_test.go

## Purpose
Regression test for report finding deduplication.

## Important APIs, Types, and Functions
TestDeduplicationInReport.

## Control Flow
Creates duplicate-title findings across tests, generates a report, and asserts one finding remains.

## State and Persistence
Uses transient Spanner/local blob through controller and reporter APIs.

## Dependencies and Integration Points
Integrates report services, discussion services, controller-created sessions/findings, report generator, and ReporterClient.

## Risks and Edge Cases
Risks include report ordering assumptions, age-window omissions in generation, and incomplete HTTP method validation.

## Test Signals
reporter/api_test.go and dedup_test.go exercise report delivery, replies, invalidation, and patch-test reports.
