<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/ackseq/ackseq.go -->
# sources/storage-engines/pebble/internal/ackseq/ackseq.go

## Purpose
This package tracks monotonically allocated sequence numbers and advances an acknowledged base only when all lower sequence numbers are acknowledged.

## Important APIs, Types, And Functions
`S` stores atomic `next`, locked `base`, and a fixed bitmap window. `New` initializes the base and next number. `Next` atomically allocates a sequence number. `Ack` marks a number, detects invalid or duplicate acknowledgements, and returns the contiguous base-advance delta. `getLocked`, `setLocked`, and `clearLocked` manipulate bitmap bits.

## Control Flow
`Next` uses atomic increment. `Ack` locks, validates `seqNum` against `[base, base+windowSize)`, rejects already-set bits, sets the bit, and then repeatedly clears bits at `base` while advancing.

## State And Persistence Behavior
State is in memory only. The fixed window covers about one million pending acknowledgements using 128 KiB. Bits are reused modulo the window as the base advances.

## Dependencies And Integration Points
It uses `sync`, `sync/atomic`, and Cockroach errors. It is suitable for commit or scheduling pipelines that need out-of-order completion with in-order publication.

## Risks And Edge Cases
Acknowledging below base, too far beyond base, or twice before base advance returns errors. The caller must not allow more than `windowSize` unacknowledged allocated numbers ahead of base.

## Test Signals
`ackseq_test.go` covers in-order, reverse-order, double-ack before and after base advance, below-base, and beyond-window cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/ackseq/ackseq.go -->
