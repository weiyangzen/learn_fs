# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/RecoveryState.h

## Purpose
`RecoveryState.h` defines the coarse recovery phase carried in `ServerDBInfo` plus a more detailed status enum used by status reporting.

## Important APIs, Types, And Functions
`enum class RecoveryState` runs from `UNINITIALIZED` through reading/locking coordinated state, recruiting, recovery transaction, writing cstate, accepting commits, all logs recruited, storage recovered, and `FULLY_RECOVERED`. `namespace RecoveryStatus` provides a detailed enum and external `names`/`descriptions` arrays.

## Control Flow
Master and cluster-controller recovery code advances through these states as it reads cluster state, locks old transaction servers, recruits roles, commits recovery mutations, publishes cstate, and waits for logs/storage recovery.

## State And Persistence Behavior
`RecoveryState` is serialized in `ServerDBInfo` and used for live system decisions. `RecoveryStatus` is primarily status output. The values form a wire/status contract.

## Dependencies And Integration Points
It depends only on Flow serialization. It integrates with master recovery, status generation, cluster controller health, and workers consuming `ServerDBInfo`.

## Risks And Edge Cases
The comment warns that `RecoveryState` is decision-bearing and should be changed cautiously. Adding states requires status descriptions and compatibility analysis.

## Test Signals
Recovery simulation should show monotonic/valid state transitions, correct status names/descriptions, and role behavior changing only at the intended recovery phases.
