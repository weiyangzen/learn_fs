# `sources/user-network-fs/go-fuse/fuse/server_linux_test.go`

## Purpose
Tests `MaxInflightRequestBytes` on Linux with blocked direct writes.

## Important APIs, Types, And Functions
Defines `blockingWriteFS` and `TestMaxInflightRequestBytesLimitsLargeWritesAndKeepsReader` with helpers for writer entry/results and reader liveness.

## Control Flow
Defines `blockingWriteFS` and `TestMaxInflightRequestBytesLimitsLargeWritesAndKeepsReader` with helpers for writer entry/results and reader liveness.

## State And Persistence
State includes blocked write channels and server reader counters. The signal ensures large writes are throttled by request bytes without starving the request reader.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State includes blocked write channels and server reader counters. The signal ensures large writes are throttled by request bytes without starving the request reader.

## Test Signals
State includes blocked write channels and server reader counters. The signal ensures large writes are throttled by request bytes without starving the request reader.
