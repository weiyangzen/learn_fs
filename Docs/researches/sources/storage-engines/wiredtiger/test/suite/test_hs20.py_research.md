# sources/storage-engines/wiredtiger/test/suite/test_hs20.py

## Purpose

Ensures reverse modifies in the history store are not reconstructed using an on-page overflow value as the wrong base.

## Important APIs, Types, and Functions

Defines `test_hs20`, key factory functions for column/string row formats, extra rollback allowance, and one workload using `leaf_value_max=10B` to force overflow values.

## Control Flow

The test inserts large overflow values at timestamp 2, appends modifies at 3 and 4, writes many additional rows to force eviction, replaces the original keys with smaller values at 5, checkpoints, then reads the timestamp 3 version of the first ten keys.

## State and Persistence Behavior

State includes overflow value storage, HS reverse modify records, eviction pressure from 100k rows, and checkpointed current disk images.

## Dependencies and Integration Points

Depends on `wiredtiger.Modify`, small-cache eviction, overflow item configuration, platform-specific stdout ignore on Darwin, and scenario generation.

## Risks and Maintenance Signals

Runtime is heavy due to 100k inserts and small cache. The test has no direct HS stat checks; correctness is historical read reconstruction.

## Test Signals

Signals are exact timestamp-3 reads of `value1 + B` for all original keys after overflow/eviction/checkpoint.
