# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/util/status.h

## Purpose
Defines `TOKUFT_STATUS_INIT`, a macro for initializing Toku engine status rows used by locktree status reporting.

## Important APIs, Types, And Functions
The macro sets row key name, column name, type, legend, include policy, and creates a partitioned counter when the status type is `STATUS_PARCOUNT`.

## Control Flow
The macro writes metadata into `array.status[k]`, applies compile-time assertions to catch invalid column-name use, sets the include mask, and conditionally calls `create_partitioned_counter`.

## State And Persistence Behavior
It initializes in-memory status row metadata and optional counter objects. There is no persistence.

## Dependencies And Integration Points
Includes `partitioned_counter.h` and is used by `LTM_STATUS_S::init()` in `standalone_port.cc`. RocksDB's range-tree manager reads initialized rows for escalation count, wait count, and current lock memory.

## Risks And Edge Cases
Macro arguments are evaluated in-place and depend on surrounding type definitions from Toku status headers. Partitioned counters allocated here must eventually be destroyed, but the standalone destroy path currently has a TODO.

## Test Signals
Status initialization tests should verify row names and counter allocation. Range lock status APIs provide indirect coverage.
