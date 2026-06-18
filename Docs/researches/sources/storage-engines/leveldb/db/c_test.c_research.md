# sources/storage-engines/leveldb/db/c_test.c

## Purpose
This C executable is the smoke and integration test for the public `leveldb/c.h` API. It validates object lifecycle, option setters, read/write/delete calls, batches, iterators, approximate sizes, properties, snapshots, repair, custom comparators, cache/env ownership, and filter policies from pure C.

## Important APIs, Types, And Functions
The file uses `leveldb_t`, comparator/cache/env/options/readoptions/writeoptions/snapshot/iterator/writebatch/filterpolicy handles, and the C functions for open/close, destroy/repair, get/put/delete/write, compaction, iteration, property lookup, approximate sizing, and memory release. Test helpers include `StartPhase`, `CheckNoError`, `CheckCondition`, `CheckEqual`, `CheckGet`, `CheckIter`, write-batch callbacks `CheckPut`/`CheckDel`, comparator callbacks, and fake filter callbacks.

## Control Flow
`main` builds all C API objects, destroys any old test DB, verifies open failure when `create_if_missing` is off, opens with options, performs puts, range compactions, batch append/iterate checks, ordered iterator navigation, bulk writes for approximate size checks, property reads, snapshot isolation, repair/reopen, and two filter-policy runs. It then destroys all API objects and prints `PASS`.

## State And Persistence Behavior
The test creates a real database in the default test directory, writes sync and non-sync records, forces compaction, closes/reopens around repair, and verifies that repair preserves surviving keys. Snapshots preserve the older `foo` value after deletion until released. The filter phase destroys and recreates the DB for custom and bloom-filter runs.

## Dependencies And Integration Points
It depends on the C wrapper over `DBImpl`, write batches, iterators, options, Env test directory, comparator/filter callback bridges, repair, and compaction APIs. It is the key compatibility signal for non-C++ users.

## Risks And Edge Cases
The test exercises ownership and `leveldb_free` paths, but it is single-threaded and does not check all option combinations. The custom filter negative-path check appears guarded by `if (phase == 0)`, comparing a string pointer to zero, so the intended fake-filter-false assertions are effectively disabled.

## Test Signals
Failures identify C ABI regressions, callback marshalling bugs, iterator ordering issues, snapshot breakage, repair problems, property/size API regressions, or object lifecycle leaks/crashes.
