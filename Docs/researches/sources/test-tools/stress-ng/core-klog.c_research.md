# sources/test-tools/stress-ng/core-klog.c

## Purpose

This Linux-specific module monitors `/dev/kmsg` during stress runs and reports kernel messages that indicate errors, lockups, OOM events, CPU throttling, hung tasks, or warnings. It can mark the overall run unsuccessful if kernel error messages are observed.

## Important APIs, Types, And Functions

Public APIs are `stress_klog_start` and `stress_klog_stop`. Internal helpers include `stress_klog_err_no_exceptions`, `stress_klog_kernel_cmdline`, and `stress_klog_convert_nl`. The static `err_exceptions` list suppresses known benign or noisy kernel messages.

## Control Flow

`stress_klog_start` resets `g_shared->klog_errors`, checks `OPT_FLAGS_KLOG_CHECK`, opens `/dev/kmsg`, forks a monitor child, seeks to the end, then reads new log messages. The child parses priority, facility, and timestamp, normalizes escaped newlines, classifies messages by content and priority, logs info or errors, dumps kernel command line once, rate-limits process dumps on lockups, increments shared error count for relevant errors, and exits when the kmsg stream ends. `stress_klog_stop` checks error count, marks `*success = false` if errors occurred, kills the monitor child, and resets shared state.

## State And Persistence Behavior

State includes static `klog_pid`, a one-shot kernel cmdline dump flag, and `g_shared->klog_errors`. The monitor child reads global kernel log state but does not mutate kernel logging. The success flag passed to stop is caller-owned.

## Dependencies And Integration Points

It depends on filesystem reads, kill/wait helpers, process naming, parent-death alarm, scheduler policy setting, process dumps, logging, global shared state, and `/dev/kmsg`. Non-Linux builds compile to no-op behavior.

## Risks And Test Signals

Risks include permission-denied access to `/dev/kmsg`, false positives/negatives in string classification, noisy kernel logs from unrelated system activity, and monitor child cleanup. Test signals include no-op without option, graceful open failure, exception filtering, escaped newline conversion, error count propagation to `success`, and child termination on stop.
