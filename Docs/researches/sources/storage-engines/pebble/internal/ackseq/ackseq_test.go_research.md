<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/ackseq/ackseq_test.go -->
# sources/storage-engines/pebble/internal/ackseq/ackseq_test.go

## Purpose
This file validates `ackseq.S` allocation and acknowledgement semantics.

## Important APIs, Types, And Functions
Tests call `New`, `Next`, and `Ack`, and assert returned deltas plus error text for invalid acknowledgements.

## Control Flow
`TestAckInOrder` expects every ack to advance by one. `TestAckOutOfOrder` allocates several numbers, acks high numbers first with zero delta, then acks the base and expects a full advance. Other tests exercise duplicate and range failures.

## State And Persistence Behavior
The tests focus on in-memory bitmap/base transitions. No persistent state is involved.

## Dependencies And Integration Points
It uses Go testing and `strings.Contains` for error classification.

## Risks And Edge Cases
The tests distinguish two duplicate-ack modes: already below base reports out-of-range, while still in-window reports already-acked. The beyond-window test acks a number that was never allocated, confirming range validation is based on base/window, not `next`.

## Test Signals
Together these tests give direct coverage of ordered and unordered acknowledgements, base advancement, bitmap clearing, and error boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/ackseq/ackseq_test.go -->
