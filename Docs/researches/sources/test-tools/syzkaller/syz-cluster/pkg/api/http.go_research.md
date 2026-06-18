# sources/test-tools/syzkaller/syz-cluster/pkg/api/http.go

## Purpose
Generic JSON and multipart HTTP helpers shared by clients and servers.

## Important APIs, Types, and Functions
getJSON, postJSON, postMultiPartFile, ReplyJSON, and ParseJSON.

## Control Flow
Client helpers build context-aware HTTP requests; server helpers enforce POST for ParseJSON and encode typed JSON responses.

## State and Persistence
No durable state; buffers JSON and multipart bodies in memory.

## Dependencies and Integration Points
Depends on Go net/http/json helpers and is integrated by controller/reporter servers plus workflow clients.

## Risks and Edge Cases
Risks include wire-contract drift, weak validation of string statuses, memory buffering for large payloads, and coarse HTTP error mapping.

## Test Signals
Covered indirectly by controller, reporter, retest, fuzzconfig, and report integration tests.
