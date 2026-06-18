# sources/test-tools/stress-ng/core-ftrace.c

## Purpose

This file implements optional Linux ftrace function profiling for stress-ng runs. When enabled, it finds the debugfs mount, enables kernel function profiling for the stress-ng PID, records start and stop function counts/times, and reports system-call-looking kernel functions invoked during the stress run.

## Important APIs, Types, And Functions

The Linux implementation is compiled only when libbsd red-black tree support, BSD `sys/tree.h`, `RB_ENTRY`, and Linux are available. `struct rb_node` stores function name, start/end call counts, and start/end microsecond totals. The red-black tree is ordered by function name via `rb_node_cmp`.

Public APIs are `stress_ftrace_start`, `stress_ftrace_stop`, `stress_ftrace_free`, and `stress_ftrace_add_pid`. Internal helpers include `stress_ftrace_debugfs_path_get`, `stress_ftrace_parse_trace_stat_file`, `stress_ftrace_parse_stat_files`, `strace_ftrace_is_syscall`, and `stress_ftrace_analyze`.

## Control Flow

`stress_ftrace_start` exits unless `OPT_FLAGS_FTRACE` is set, initializes the tree, checks `CAP_SYS_ADMIN`, locates debugfs via mounted filesystem inspection, disables profiling, clears and sets `set_ftrace_pid`, enables `function_profile_enabled`, parses initial trace stats, and marks tracing enabled. `stress_ftrace_stop` clears PIDs, disables profiling, parses final trace stats, and analyzes deltas. `stress_ftrace_analyze` walks the tree, computes positive deltas, filters names that look like syscall wrappers, and logs counts and time.

On unsupported builds, exported functions are stubs; `stress_ftrace_start` logs a not-implemented message when requested.

## State And Persistence Behavior

State is process-global: a static red-black tree, a cached debugfs path, and `tracing_enabled`. Kernel tracing state is external and must be restored by disabling profiling and clearing `set_ftrace_pid`. `stress_ftrace_free` frees all tree nodes and should be called during cleanup to avoid leaks.

## Dependencies And Integration Points

This module depends on capabilities, mount enumeration, filesystem file-write helpers, logging, shim string utilities, debugfs layout, and Linux ftrace files under `debugfs/tracing`. It integrates with the global option flag system and process lifecycle around stressor execution.

## Risks And Test Signals

Risks include leaving ftrace enabled, failing under restricted containers, missing debugfs, changed trace-stat formats, out-of-memory while building the tree, and false syscall classification. Useful signals are graceful no-op behavior without capability/debugfs, correct PID filtering, positive delta reporting after a known workload, and cleanup that empties the tree and disables profiling.
