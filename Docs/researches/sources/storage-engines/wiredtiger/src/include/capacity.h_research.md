<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/capacity.h -->
# sources/storage-engines/wiredtiger/src/include/capacity.h

## Purpose
Defines capacity-throttling types, constants, subsystem percentages, and reservation state for limiting WiredTiger read/write throughput. It centralizes the shared budget model for checkpoint, eviction, log, read, and total capacity scheduling.

## Important APIs, Types, and Functions
`WT_THROTTLE_TYPE` classifies throttled operations as checkpoint, eviction, logging, or read.

Constants define minimum configured capacity (`WT_THROTTLE_MIN`), background fsync thresholds (`WT_CAPACITY_FILE_THRESHOLD`, `WT_CAPACITY_MIN_THRESHOLD`, `WT_CAPACITY_PCT`), small-sleep cutoff (`WT_CAPACITY_SLEEP_CUTOFF_US`), and subsystem percentage allocation (`WT_CAP_CKPT`, `WT_CAP_EVICT`, `WT_CAP_LOG`, `WT_CAP_READ`) via `WT_CAPACITY_SYS`.

`WT_THROTTLE` stores per-subsystem bytes-per-second budgets, total capacity, threshold period, bytes written in the current period, signal state, and atomic next-reservation timestamps for each subsystem plus the total stream.

## Control Flow
This header is declarative. Runtime throttling code will compute subsystem budgets from total capacity, reserve future nanosecond slots in the relevant subsystem and total reservation fields, and sleep when the reservation lies in the future. Very short sleeps below the cutoff can be ignored to reduce overhead at the cost of temporary burstiness.

## State and Persistence Behavior
Capacity state is in-memory and shared across threads. It does not persist data itself, but it regulates the rate at which checkpoint, eviction, log, and read I/O reach the filesystem or storage service. `written` and reservation fields are volatile/shared counters for the active period.

## Dependencies and Integration Points
Depends on common size constants, atomic/shared-field conventions, and the capacity server/throttling implementation elsewhere. Integration points are checkpoint writes, eviction writes, logging, reads, background fsync signaling, and any stats or configuration code that exposes capacity limits.

## Risks and Edge Cases
Subsystem percentages intentionally sum over 100 because not all subsystems peak simultaneously; total capacity must still be enforced separately. Ignoring sleeps shorter than `WT_CAPACITY_SLEEP_CUTOFF_US` can create bursty I/O. Reservation timestamps must be updated atomically to avoid overbooking under concurrency. Thresholds that are too small can cause excessive wakeups or poor smoothing.

## Test Signals
Relevant tests should configure capacity limits and verify throttled checkpoint/log/read/eviction throughput, total-budget enforcement when subsystems overlap, no-throttle behavior below minimum/disabled settings, small-sleep cutoff behavior, and background fsync signaling thresholds.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/include/capacity.h -->
