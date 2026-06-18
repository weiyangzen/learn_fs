# sources/test-tools/syzkaller/syz-cluster/pkg/reporter/generator.go

## Purpose
Background generator for SessionReport rows.

## Important APIs, Types, and Functions
ReportGenerator, NewGenerator, Loop, Process, generateReportsPeriod/Limit, relevantReportAge.

## Control Flow
Periodically queries finished sessions missing reports, then inserts moderation or job-specific reports.

## State and Persistence
Persists SessionReports and reads Sessions/Jobs.

## Dependencies and Integration Points
Integrates report services, discussion services, controller-created sessions/findings, report generator, and ReporterClient.

## Risks and Edge Cases
Risks include report ordering assumptions, age-window omissions in generation, and incomplete HTTP method validation.

## Test Signals
reporter/api_test.go and dedup_test.go exercise report delivery, replies, invalidation, and patch-test reports.
