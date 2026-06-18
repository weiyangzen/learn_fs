# sources/test-tools/syzkaller/syz-cluster/pkg/api/urls.go

## Purpose
Dashboard URL construction helper.

## Important APIs, Types, and Functions
URLGenerator and methods for finding log/repro links, series/session pages, build config/log links, and job patch links.

## Control Flow
Each method formats baseURL plus a fixed route template.

## State and Persistence
No persistence; generated links are embedded into API responses and emails.

## Dependencies and Integration Points
Depends on Go net/http/json helpers and is integrated by controller/reporter servers plus workflow clients.

## Risks and Edge Cases
Risks include wire-contract drift, weak validation of string statuses, memory buffering for large payloads, and coarse HTTP error mapping.

## Test Signals
Covered indirectly by controller, reporter, retest, fuzzconfig, and report integration tests.
