# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_boottrace.c

## Purpose
Implements boot-time, runtime, and shutdown tracing tables for kernel and userland milestones. Trace data is exposed through `kern.boottrace` sysctls and optional console dumping.

## Key Elements
- Event record: `struct bt_event`.
- Table state: `struct bt_table`.
- Tables: `bt` for boot, `rt` for runtime, `st` for shutdown.
- Default sizes: boot 3000, runtime 2000, shutdown 1000, minimum 500.
- Global enable: `boottrace_enabled`, tunable/sysctl `kern.boottrace.enabled`.
- Public functions: `boottrace()`, `boottrace_dump_console()`, `boottrace_reset()`, `boottrace_resize()`.

## Event Data
Each event records:
- Cycle counter and kernel tick timestamp.
- CPU id.
- Current pid.
- Process/thread name.
- Event name.
- Process CPU time and block I/O counters when safe to fetch.

`dotrace()` is lockless and uses atomic compare-and-set on the table cursor so it can be called from interrupt-sensitive paths. Runtime traces wrap; boot and shutdown traces drop entries once full.

## Sysctl Interface
The file defines sysctls under `kern.boottrace`:
- `log`: read formatted boot/runtime trace log.
- `boottrace`: write a boot event.
- `runtrace`: write a runtime event and mark boot complete.
- `shuttrace`: write a shutdown event and mark shutdown tracing active.
- `reset`: reset runtime tracing by recording a reset event.
- `shutdown_trace`: console dumping control.
- `shutdown_trace_threshold`: minimum delta threshold for selective shutdown console output.
- `table_size`: boot table tunable.

User messages may be `thread:event`; otherwise the current process name is used.

## Display Behavior
`boottrace_display()` walks the circular table from the current cursor, prints event deltas in milliseconds, and can filter output by delta threshold. It also prints total measured time across the displayed trace.

`boottrace_dump_console()` dumps shutdown trace data during shutdown/reboot/panic, otherwise boot and runtime tables.

## Initialization
`boottrace_init()` runs at `SI_SUB_CPU`. If tracing is enabled, it allocates all three tables, creates an initial boot event, enables runtime wraparound, and leaves shutdown tracing non-wrapping.

## Research Notes
Because tracing is optional and disabled by default, users must enable it via tunables early enough for boot capture. Early events before table allocation are counted as `drops_early`.
