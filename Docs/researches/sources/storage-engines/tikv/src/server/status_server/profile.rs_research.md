# sources/storage-engines/tikv/src/server/status_server/profile.rs

## Purpose

This module backs the status server's profiling endpoints. It creates one-shot heap profiles, runs bounded CPU profiles, normalizes thread names in pprof output, reads generated files, and optionally converts heap profiles to SVG through an embedded `jeprof` script.

## Important APIs, Types, And Functions

`dump_one_heap_profile` creates a `NamedTempFile` and calls `tikv_alloc::dump_prof` or the test stub. `start_one_cpu_profile` enforces at most one concurrent CPU profile through `CPU_PROFILE_ACTIVE`, starts a `pprof::ProfilerGuard`, waits for a caller-supplied future, then emits either protobuf or flamegraph SVG bytes. `ProfileRunner<I, T>` is a generic future wrapper that pairs `on_start`, an async end condition, and `on_end` cleanup/report generation. `read_file` reads a path into bytes, and `jeprof_heap_profile` spawns Perl with embedded `jeprof.in` and the current TiKV executable. `extract_thread_name` strips numeric suffixes and normalizes spaces/underscores to dashes.

## Control Flow

CPU profiling starts by checking the global mutex-protected active flag. The profile guard is constructed with frequency and a blocklist for common system libraries. When the end future resolves, `on_end` clears the active flag through `defer!`, builds the pprof report with a frames post-processor, and serializes the selected format. If the end future fails, that error wins over report generation. Heap profiling is simpler: create temp file, dump allocator profile, return the file for the HTTP layer to read or post-process.

## State And Persistence Behavior

The only durable side effect is temporary profile file creation; the `NamedTempFile` lifetime controls cleanup. CPU profile concurrency is process-global state in `CPU_PROFILE_ACTIVE`. `jeprof_heap_profile` runs a child process and captures stdout/stderr without persisting the SVG itself.

## Dependencies And Integration Points

The module depends on `pprof`, protobuf encoding through `pprof::protos::Message`, `tikv_alloc`, `tempfile`, regex normalization, and `tikv_util::defer`. It is consumed by `status_server/mod.rs` for `/debug/pprof/heap` and `/debug/pprof/profile`.

## Risks And Edge Cases

Only one CPU profile can run process-wide; concurrent requests return `Already in CPU Profiling`. The active flag is cleared only after `on_end`, so panics in that path would risk wedging profiling. `jeprof_heap_profile` assumes Perl can run and that the embedded script accepts `/dev/stdin`; this may be environment-sensitive. Thread name normalization is regex based and can leave unfamiliar names unchanged.

## Test Signals

Tests validate thread-name extraction for common TiKV thread prefixes and verify that a second CPU profile request is rejected while the first is active. The heap dump function is stubbed in tests to avoid requiring heap profiling support.
