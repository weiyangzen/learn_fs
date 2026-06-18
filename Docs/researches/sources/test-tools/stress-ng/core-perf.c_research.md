# sources/test-tools/stress-ng/core-perf.c

Purpose: implements optional Linux perf counter collection and reporting for stressor runs.

Important APIs/functions: `stress_perf_init`, `stress_perf_open`, `stress_perf_enable`, `stress_perf_disable`, `stress_perf_close`, and `stress_perf_stat_dump`. Internal helpers resolve tracepoint IDs, wrap `perf_event_open`, sanitize YAML labels, scale rates, and compute relative metrics.

Control flow: `stress_perf_init` resolves tracepoint configs from debugfs. `stress_perf_open` initializes fds and opens hardware/software/tracepoint events for the current process with inheritance. Enable/disable use perf ioctls. Close reads counters plus time enabled/running and scales multiplexed values. Dump aggregates per-stressor instance counters and writes human-readable plus YAML output.

State/persistence: per-stressor `stress_perf_t` stores fds/counters. Shared `g_shared->perf.no_perf` suppresses repeated failed attempts behind a lock. No durable persistence except YAML/log output.

Dependencies/integration: Linux `perf_event_open`, perf headers, syscall support, `core-perf.h`, `core-lock.h`, stressor stats lists, logging/YAML helpers, locale formatting, debugfs, and procfs.

Risks: perf permissions commonly block users; tracepoint paths vary by kernel; many fds can be opened per stressor; static formatting buffers are not thread-safe; duration zero affects per-second output; unsupported builds compile out implementation.

Test signals: privileged/unprivileged perf runs, high `perf_event_paranoid`, missing debugfs tracepoints, counter multiplex scaling, YAML output, multi-instance aggregation, and no-perf fallback messaging.
