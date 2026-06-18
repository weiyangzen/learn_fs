# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/DataMovement.h

## sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/DataMovement.h

Purpose: declares conversion helpers between data movement reasons and priority integers.

Important APIs: `dataMovementPriority(DataMovementReason)` and `priorityToDataMovementReason(int)`.

Control flow and state: this header only declares mappings; implementation elsewhere must keep the two functions inverse for supported priorities.

Dependencies and integration: depends on `fdbclient/SystemData.h` for `DataMovementReason`. Data distributor and movement metadata code use priorities to schedule and explain relocation work.

Risks and tests: mismatched reason/priority mappings can cause wrong scheduling, confusing traces, or bad repair priority. Tests should cover every enum value, unknown priorities, and round-trip conversion.
