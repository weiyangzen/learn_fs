# sources/test-tools/stress-ng/core-log.c

## Purpose

This module implements stress-ng logging: stdout/stderr/log-file/syslog routing, severity filtering, timestamping, brief output, skip-message handling, per-process block buffering, and failure-count driven abort behavior.

## Important APIs, Types, And Functions

Static state includes `abort_fails`, `abort_msg_emitted`, `log_fd`, and a per-process `pr_msg_buf_t` that accumulates block-buffered messages. Public APIs are `pr_fd`, `pr_block_begin`, `pr_block_end`, `pr_fail_check`, `pr_yaml`, `pr_closelog`, `pr_openlog`, and severity functions `pr_dbg`, `pr_dbg_skip`, `pr_inf`, `pr_inf_skip`, `pr_err`, `pr_err_skip`, `pr_fail`, `pr_tidy`, `pr_warn`, `pr_warn_skip`, and `pr_metrics`. Internal helpers include `pr_log_write_buf_fd`, `pr_log_write_buf`, `pr_log_write`, and `pr_msg`.

## Control Flow

Severity wrappers build a `va_list` and call `pr_msg`. `pr_msg` checks `g_pr_log_flags`, optional skip suppression in the wrapper functions, formats the message with optional timestamp and prefix, writes to the log file and selected stdout/stderr fd, and mirrors non-debug messages to syslog where enabled. `pr_fail` increments `abort_fails`; after `ABORT_FAILURES` failures, one abort message is emitted and the global continue flag is cleared. `pr_block_begin/end` buffer messages for a matching process and flush them as one write unless lockless logging is enabled. `pr_yaml` writes formatted YAML to a specific file handle.

## State And Persistence Behavior

State includes global log flags, optional log file descriptor, failure abort counters, a per-process block buffer, and syslog use through libc. Log file output persists to the configured file until `pr_closelog`. Five `pr_fail` messages can alter global run state by clearing the continue flag, and `pr_fail_check` converts a successful return code to failure if the abort threshold was reached.

## Dependencies And Integration Points

It depends on core logging flags from `core-log.h`, global program/log state, builtin shims, syslog support, time formatting, and shared interrupt state for `pr_tidy` signal-aware severity selection. It is used by nearly every other module for diagnostics and result reporting.

## Risks And Test Signals

Risks include large buffered blocks consuming memory, partial writes to terminal or log files, timestamp formatting errors, unintended run cancellation after repeated `pr_fail`, and stdout/stderr routing mistakes. Test signals include flag filtering, skip-silent behavior, brief mode prefixes, timestamp output, file open/close and fsync, syslog calls under enabled flags, YAML formatting, block buffering, and abort threshold propagation through `pr_fail_check`.
