# sources/storage-engines/rocksdb/util/thread_operation.h

## Purpose

Defines global metadata tables mapping `ThreadStatus` operation, stage, state, and property enum values to human-readable names.

## APIs, control flow, and state

When thread status is enabled, the header declares `OperationInfo`, `OperationStageInfo`, `StateInfo`, and `OperationProperty`, plus static arrays for operation names, operation stages, state names, compaction properties, and flush properties. When `NROCKSDB_THREAD_STATUS` is defined, placeholder empty structs are provided.

## Dependencies and integration

It depends on `rocksdb/thread_status.h`. `ThreadStatusUpdater` stores pointers into these static tables, and `thread_list_test.cc` validates array indexing against enum values.

## Risks and test signals

The main risk is enum/table drift: the arrays must preserve exact order and cardinality expected by `ThreadStatus` enums. `ThreadListTest.GlobalTables` directly checks operation, state, and stage tables.
