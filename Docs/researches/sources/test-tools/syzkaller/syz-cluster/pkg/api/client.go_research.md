# sources/test-tools/syzkaller/syz-cluster/pkg/api/client.go

## Purpose
Controller-facing HTTP client used by workflow steps and tests.

## Important APIs, Types, and Functions
NewClient plus methods for series/session/job retrieval, tree config, build/test/finding/base-finding uploads, artifact upload, previous finding lookup, test-step upload, and job submission.

## Control Flow
Methods format REST paths and call generic JSON or multipart helpers. finishRequest uses a one-minute http.Client, enforces HTTP 200, and decodes JSON.

## State and Persistence
Stateless except baseURL; persistence occurs behind controller services.

## Dependencies and Integration Points
Depends on Go net/http/json helpers and is integrated by controller/reporter servers plus workflow clients.

## Risks and Edge Cases
Risks include wire-contract drift, weak validation of string statuses, memory buffering for large payloads, and coarse HTTP error mapping.

## Test Signals
Covered indirectly by controller, reporter, retest, fuzzconfig, and report integration tests.
