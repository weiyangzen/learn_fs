# sources/test-tools/syzkaller/pkg/fuzzer/queue/queue_test.go

## Purpose
This file tests core queue behavior: FIFO ordering, dynamic priority ordering, glob output parsing, and tee request copying.

## Important APIs, Types, And Functions
`TestPlainQueue` verifies `PlainQueue.Submit`/`Next`. `TestPrioQueue` exercises `DynamicOrderer.Append` priority ordering. `TestGlobFiles` checks nul-separated output parsing. `TestTee` checks that `Tee` returns the original request and submits a sanitized copy to the duplicate queue.

## Control Flow
Tests submit requests, call `Next`, and compare identity or field values. `TestTee` builds a program request with fields that should and should not be copied, then inspects the duplicate request.

## State And Persistence Behavior
Tests exercise in-memory queue state and do not persist data.

## Dependencies And Integration Points
The file uses `flatrpc`, `prog`, and `testify/assert`. It covers primitives used by fuzzer execution scheduling and side-channel duplicate execution.

## Risks
No tests cover `Deduplicate`, `DefaultOpts`, `DynamicSourceCtl`, `Alternate`, `Callback`, or `RandomQueue` in this file.

## Test Signals
Assertions lock in FIFO order, low-priority-number-first dynamic ordering, nil/nonnull glob parsing, and tee dropping `ReturnOutput`/`Important` while copying type/options/program identity data.
