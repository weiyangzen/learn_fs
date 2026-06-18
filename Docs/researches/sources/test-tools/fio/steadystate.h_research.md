# sources/test-tools/fio/steadystate.h

## Purpose
`steadystate.h` declares steady-state configuration/state and public helpers used by fio job setup, periodic checking, and statistics reporting.

## Important APIs, Types, And Functions
`struct steadystate_data` stores limit, duration, ramp time, state flags, ring-buffer head/tail, IOPS/bandwidth/latency data buffers, computed slope/deviation/criterion, regression sums, previous sample time/counters, and previous latency accumulators. It declares allocation/free/check/init/reporting helpers and exposes `steadystate_enabled` and `ss_check_interval`.

The enum values define bit positions and masks for IOPS, bandwidth, slope mode, attained/ramp/data state, percent criterion, buffer-full state, latency mode, and combined slope presets.

## Control Flow
Job initialization fills `steadystate_data`; setup allocates buffers; runtime checks mutate the ring and may terminate jobs; final stats copy steady-state fields into `thread_stat` and call mean helpers.

## State And Persistence Behavior
All state is per thread or per reporting group and in-memory. Data pointers are later mirrored into `thread_stat` for output and network transport.

## Dependencies And Integration Points
The header includes `thread_options.h` and is consumed by `steadystate.c`, `stat.c`, and server stat serialization. Its flag definitions must align with job option parsing and report rendering.

## Risks And Edge Cases
The bitmask API allows invalid combinations unless option parsing rejects them. Duration and interval units are not self-evident from the struct alone, so callers must follow initialization conventions.

## Test Signals
Tests should assert expected flag combinations, initialized default state, mean helper behavior, and compatibility between option parser state bits and report output.
