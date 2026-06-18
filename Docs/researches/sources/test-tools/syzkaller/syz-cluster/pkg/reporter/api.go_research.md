# sources/test-tools/syzkaller/syz-cluster/pkg/reporter/api.go

## Purpose
Reporter HTTP server for report delivery workflow.

## Important APIs, Types, and Functions
APIServer, NewAPIServer, Mux, upstreamReport, invalidateReport, nextReports, confirmReport, recordReply, reply, TestServer.

## Control Flow
Routes parse requests, call ReportService/DiscussionService, and centralize error-to-status mapping.

## State and Persistence
Server is stateless; services mutate reports, findings, and replies in Spanner.

## Dependencies and Integration Points
Integrates report services, discussion services, controller-created sessions/findings, report generator, and ReporterClient.

## Risks and Edge Cases
Risks include report ordering assumptions, age-window omissions in generation, and incomplete HTTP method validation.

## Test Signals
reporter/api_test.go and dedup_test.go exercise report delivery, replies, invalidation, and patch-test reports.
