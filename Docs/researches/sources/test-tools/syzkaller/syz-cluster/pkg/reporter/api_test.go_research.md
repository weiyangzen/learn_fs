# sources/test-tools/syzkaller/syz-cluster/pkg/reporter/api_test.go

## Purpose
End-to-end reporter API tests.

## Important APIs, Types, and Functions
Tests cover report flow, reply recording, invalidation, patch-test reports, triage skip, and failed-step infrastructure errors.

## Control Flow
Creates controller-side sessions/findings, runs ReportGenerator, then uses ReporterClient against httptest reporter server.

## State and Persistence
Exercises report, reply, job, session, finding, test, and step rows.

## Dependencies and Integration Points
Integrates report services, discussion services, controller-created sessions/findings, report generator, and ReporterClient.

## Risks and Edge Cases
Risks include report ordering assumptions, age-window omissions in generation, and incomplete HTTP method validation.

## Test Signals
reporter/api_test.go and dedup_test.go exercise report delivery, replies, invalidation, and patch-test reports.
