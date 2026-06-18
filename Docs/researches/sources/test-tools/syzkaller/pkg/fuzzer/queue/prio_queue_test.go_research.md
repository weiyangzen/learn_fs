# sources/test-tools/syzkaller/pkg/fuzzer/queue/prio_queue_test.go

## Purpose
This file unit-tests the generic priority queue wrapper.

## Important APIs, Types, And Functions
`TestPrioQueueOrder` constructs `priorityQueueOps[int]`, pushes values with priorities 1, 3, and 2, then pops and checks values.

## Control Flow
The test exercises heap insertion, ordered removal, empty pop, and final length.

## State And Persistence Behavior
All state is local heap memory.

## Dependencies And Integration Points
It uses `testify/assert`. It validates the primitive used by `DynamicOrderer`.

## Risks
The test does not cover equal priorities or non-int payloads, but generic behavior is independent of payload type.

## Test Signals
Expected pop sequence is 1, 2, 3, then zero on empty with length zero.
