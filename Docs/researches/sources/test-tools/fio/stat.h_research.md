# sources/test-tools/fio/stat.h

## Purpose
`stat.h` defines fio's statistics data model, constants, macros, and public stat/reporting API. It is shared by local reporting, backend server serialization, JSON/terse output, and consumers that update per-I/O counters.

## Important APIs, Types, And Functions
`struct group_run_stats` stores per-direction run time, bandwidth extrema, I/O bytes, aggregate bandwidth, base/unit formatting, group id, significant figures, and unified read/write reporting mode. `struct thread_stat` is the packed central per-job/per-group statistics record, including names/errors, latency stats, bandwidth/IOPS stats, rusage, I/O depth maps, latency buckets, totals, errors, block lifetime data, unit formatting, ZBD stats, latency-target state, steady-state fields and data pointers/offsets, per-priority latency stats, and cache hit/miss counts.

Macros define latency bucket sizes, percentile-list size, trim block-info encoding, job name/description sizes, and unified reporting modes. `struct jobs_eta` and `struct jobs_eta_packed` define ETA payload shape. `struct clat_prio_stat` stores a per-priority latency histogram plus summary stat.

Public functions include stat lifecycle, ETA/status display, aggregation, initialization, percentile calculation, distribution calculation, sample addition, log handling, per-priority allocation/free, disk-util output, and `io_u_block_info()`.

## Control Flow
Workers update `thread_stat` through stat.c functions during I/O. Reporting code initializes and sums `thread_stat`/`group_run_stats`, then prints locally or serializes over the server protocol. Inline helpers `nsec_to_usec()` and `nsec_to_msec()` normalize display units.

## State And Persistence Behavior
The header declares `stat_sem`, `agg_io_log[]`, and `write_bw_log`. `thread_stat` contains pointer/offset unions so the same packed struct can represent in-process pointers or network payload offsets for steady-state/per-priority arrays.

## Dependencies And Integration Points
It includes `iolog.h`, `lib/output_buffer.h`, `diskutil.h`, and `json.h`. It is directly embedded in `server.h` network PDUs, so layout changes require protocol conversion updates.

## Risks And Edge Cases
`struct thread_stat` and `group_run_stats` are packed and networked, so alignment, endian conversion, pointer-size assumptions, and field additions are high-risk. Fixed array sizes such as `MAX_NR_BLOCK_INFOS` cap collected detail. The pointer/offset unions are powerful but easy to misuse if code reads a network offset as an in-process pointer.

## Test Signals
ABI tests should check expected struct sizes/offsets and protocol conversion coverage. Functional tests should verify percentile constants, block-info macros, unit conversion helpers, initialization minima, and per-priority allocation/reporting behavior.
