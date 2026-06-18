## sources/test-tools/stress-ng/stress-uprobe.c

Purpose: Implements `uprobe`, generating Linux uprobe trace events on a libc function to stress kernel tracing.

Important APIs/types/functions: `stress_uprobe_info`, `stress_uprobe_supported`, `stress_uprobe_write`, `stress_uprobe_libc_start`, and `stress_uprobe`; uses `/proc/$pid/maps`, debugfs tracing files, `select`, `read`, and `getpid` calls as event triggers.

Control flow: support rejects static builds and requires `CAP_SYS_ADMIN`. Runtime locates libc text base, computes the offset of `getpid`, creates a unique uprobe event under `/sys/kernel/debug/tracing/uprobe_events`, enables it, clears the trace, calls `getpid` repeatedly, reads `trace_pipe`, and counts occurrences of the event name.

State and persistence: manipulates global tracing/debugfs state; cleanup disables uprobe events and removes the named event each loop. Metrics track trace bytes.

Dependencies/integration: Linux-only debugfs tracing, libc mapping format, stress-ng capability checks and metrics.

Risks: intrusive tracing side effects; debugfs permissions/availability, busy trace_pipe, or libc path parsing can skip the stressor. Event parsing is intentionally quick and can undercount across read boundaries.

Test signals: bogo count equals parsed event hits; reports MB trace data per second.
