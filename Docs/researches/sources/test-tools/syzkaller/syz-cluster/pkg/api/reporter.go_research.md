# sources/test-tools/syzkaller/syz-cluster/pkg/api/reporter.go

## Purpose
Reporter-service client and reply/report request contracts.

## Important APIs, Types, and Functions
ReporterClient, NextReportResp, UpstreamReportReq, RecordReplyReq/Resp, LKMLReporter, GetNextReport, ConfirmReport, UpstreamReport, InvalidateReport, RecordReply.

## Control Flow
Builds /reports routes and delegates to postJSON; reply recording maps email message IDs to report IDs.

## State and Persistence
Stateless client; server mutates report, finding, and reply records.

## Dependencies and Integration Points
Depends on Go net/http/json helpers and is integrated by controller/reporter servers plus workflow clients.

## Risks and Edge Cases
Risks include wire-contract drift, weak validation of string statuses, memory buffering for large payloads, and coarse HTTP error mapping.

## Test Signals
Covered indirectly by controller, reporter, retest, fuzzconfig, and report integration tests.
