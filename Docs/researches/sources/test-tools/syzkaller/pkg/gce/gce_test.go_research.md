# sources/test-tools/syzkaller/pkg/gce/gce_test.go

## Purpose
This file unit-tests deterministic helper behavior in the GCE wrapper without calling real cloud APIs.

## Important APIs, Types, And Functions
`TestValidateZone` checks valid zone strings and rejects a region-only name. `TestZoneToRegion` checks region extraction from common and multi-part region names. `TestDiskSizeGB` checks special C4A disk sizing. `TestLocalZone` uses an `httptest.Server` to emulate metadata zone output. `TestZoneListPrioritization` exercises zone score sorting, success, preemption, insertion failure, and repeated success.

## Control Flow
The metadata test replaces `Context.metadataServer` with the test server URL and calls `localZone`. The zone-list test initializes equal scores, sorts, mutates scores through record methods, and asserts the expected list order after each step.

## State And Persistence Behavior
All state is in-memory test data. The HTTP server provides transient metadata response only.

## Dependencies And Integration Points
The tests use `net/http/httptest` and `testify/assert`. They cover helper functions used by real `NewContext` and VM creation.

## Risks
No tests mock `compute.Service`, so create/delete image/instance paths, operation waiting, API rate-limit handling, and resource exhaustion fallback are untested in this file.

## Test Signals
Assertions lock in zone regex behavior, region parsing, disk-size policy, metadata path handling, and zone score decay/reward ordering.
