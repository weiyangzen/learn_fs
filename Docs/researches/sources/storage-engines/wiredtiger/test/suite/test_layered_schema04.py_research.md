# sources/storage-engines/wiredtiger/test/suite/test_layered_schema04.py

## Purpose

This long test stress-tests schema creation by creating a large number of layered tables. It is aimed at file-id allocation, metadata scaling, and resource handling for many disaggregated layered objects.

## Important APIs, Types, and Functions

The class uses `disagg_test_class`, `gen_disagg_storages(..., disagg_only=True)`, and a leader connection with statistics and statistics logging. The single `test_create_tables` method is marked with `wttest.longtest('lots of tables')` and loops over 10,000 `session.create` calls.

## Control Flow

For each index from 0 to 9999, the test creates `layered:test_table<i>` with string key/value formats and asserts `session.create` returns zero. There are no writes, scans, checkpoints, or drops in the test body; its purpose is creation throughput and schema scalability.

## State, Persistence, and Dependencies

The persistent state is the metadata and component files for 10,000 layered tables in one leader home. Dependencies are `wttest`, `helper_disagg`, and generated disaggregated storage scenarios. The test integrates with layered table creation, metadata table growth, and any storage-source file naming/allocation behavior under high object count.

## Risks and Test Signals

Risks include metadata exhaustion, duplicate names or IDs, handle leaks, slow path failures, and object-count limits in disaggregated schema code. The test signal is simple but high volume: every create must return success. Because it is marked long, it may not run in short suites and is best treated as a stress signal.
