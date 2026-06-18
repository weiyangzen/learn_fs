# sources/user-network-fs/nfs-utils/support/nfs/xlog.c

Purpose: process-wide logging and debug-facility control for nfs-utils support code.

Important APIs and globals: `xlog_open()`, `xlog_stderr()`, `xlog_syslog()`, `xlog_config()`, `xlog_sconfig()`, `xlog_set_debug()`, `xlog_enabled()`, `xlog_backend()`, `xlog()`, `xlog_warn()`, `xlog_err()`, and `xlog_errno()`. `export_errno` is set for error/general debug calls.

Control flow: `xlog_open()` opens syslog and installs SIGUSR1/SIGUSR2 toggles. SIGUSR1 progressively enables debug masks; SIGUSR2 disables debug logging. `xlog_backend()` filters debug/nonfatal messages, prints to stderr and/or syslog, maps severity to syslog priority, and exits for `L_FATAL`.

State and persistence: global flags control stderr/syslog output, debug mask, program name, pid, and exported error flag. No file persistence except syslog side effects.

Dependencies and integration: widely used by support libraries and daemons. Reads debug config via `conf_get_list(service, "debug")`.

Risks: signal handlers call logging code that is not async-signal-safe. Global mutable logging state is not thread-safe. `va_list` is consumed for stderr and then reused for syslog only if stderr path did not consume it; current code uses `va_copy` for stderr, so syslog still receives the original list. Fatal logging exits from library contexts.

Test signals: stderr/syslog toggles, debug facility parsing, config-driven debug, SIGUSR1/SIGUSR2 behavior, `L_FATAL` exit, and `export_errno` updates.
