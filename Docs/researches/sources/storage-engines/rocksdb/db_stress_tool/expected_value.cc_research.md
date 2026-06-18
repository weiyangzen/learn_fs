# sources/storage-engines/rocksdb/db_stress_tool/expected_value.cc

## Purpose
`expected_value.cc` implements transitions and helper predicates for the compact `ExpectedValue` bitfield used by db_stress expected-state tracking.

## Important APIs, types, and functions
The file implements `ExpectedValue::Put()`, `Delete()`, `SyncPut()`, `SyncPendingPut()`, `SyncDelete()`, `GetFinalValueBase()`, `GetFinalDelCounter()`, and the `ExpectedValueHelper` predicates `MustHaveNotExisted()`, `MustHaveExisted()`, and `InExpectedValueBaseRange()`.

## Control flow
`Put(true)` only marks pending write. `Put(false)` advances the value base, clears deleted, and clears pending write. `Delete(true)` refuses to create a pending delete when the key does not currently exist; otherwise it marks pending delete. `Delete(false)` advances the deletion counter, marks deleted, and clears pending delete. `SyncPut()` overwrites the value base from recovery/scan input, clears deleted and pending write, and also clears pending delete to recover from crashes during delete. `SyncDelete()` performs a final delete and clears pending write to recover from crashes during put.

Helper predicates compare a pre-read and post-read expected value. `MustHaveNotExisted()` requires the key to be deleted before the read and no write to have completed through the post-read final value base. `MustHaveExisted()` requires the key to be not deleted before the read and no delete to have completed through the post-read final delete counter. `InExpectedValueBaseRange()` accepts value-base wraparound at the 15-bit mask boundary.

## State and persistence behavior
All state is stored in the caller-owned `uint32_t` bitfield. This file does not persist directly, but its transitions determine the bytes stored by `ExpectedState` in memory or mmap files. The final-value helpers intentionally account for pending operations so readers can validate concurrent observations.

## Dependencies and integration points
The implementation depends on `expected_value.h` and `<atomic>` for fences used in the companion pending-value class. It is used by expected-state preparation, DB read validation, trace replay, and crash-recovery reconciliation.

## Risks and test signals
Boundary behavior matters: value bases wrap inside `VALUE_BASE_MASK` and deletion counters wrap inside `DEL_COUNTER_MASK`. Pending state must be cleared correctly on sync recovery paths or verification can report false positives after crashes. Unit tests should cover missing-key pending delete rejection, pending/final transitions, crash sync helpers, helper predicates across concurrent write/delete windows, and value-base wraparound.
