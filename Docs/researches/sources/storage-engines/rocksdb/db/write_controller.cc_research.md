# sources/storage-engines/rocksdb/db/write_controller.cc

Purpose: This file implements write-stall and write-delay control. It provides RAII token creation/destruction and a byte-credit delay algorithm used when compaction pressure requires throttling writes.

Important APIs/types/functions: Implemented methods are `GetStopToken`, `GetDelayToken`, `GetCompactionPressureToken`, `IsStopped`, `GetDelay`, `NowMicrosMonotonic`, and destructors for `StopWriteToken`, `DelayWriteToken`, and `CompactionPressureToken`.

Control flow: Token creation increments the corresponding atomic counter and returns a token whose destructor decrements it. Starting the first delay token resets `next_refill_time_` and `credit_in_bytes_`, then clamps the requested delayed write rate. `GetDelay` returns zero if stopped or not delayed, spends available byte credit if possible, refills credit every 1ms based on elapsed monotonic time and delayed rate, and otherwise computes a sleep duration sufficient to bring the write back under budget with a minimum 1ms delay.

State and persistence behavior: The controller is in-memory DB state. Counters represent active reasons to stop, delay, or speed up compaction. Delay state consists of `credit_in_bytes_`, `next_refill_time_`, and `delayed_write_rate_`. No data is persisted, but the state directly gates write throughput.

Dependencies and integration points: It depends on `db/write_controller.h` and `rocksdb/system_clock.h`. It is used by DB/column-family write stall management, compaction pressure logic, and callers that hold the DB mutex before token operations and delay calculation.

Risks: Comments require DB mutex for all methods including token destruction, but counters are atomic and some loads are relaxed; misuse outside the mutex can still race on non-atomic credit/refill fields. The delay algorithm assumes the caller sleeps for the returned duration. Changing rates while debt exists applies the new rate only to later calculations.

Test signals: No direct test file is in this work item, so coverage is likely through DB write-stall tests elsewhere. Assertions guard token underflow in destructors.
