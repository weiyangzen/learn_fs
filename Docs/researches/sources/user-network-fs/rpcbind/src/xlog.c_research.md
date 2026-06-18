<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/xlog.c -->
# sources/user-network-fs/rpcbind/src/xlog.c

Purpose: Provides rpcbind's lightweight logging backend with syslog/stderr selection, debug facility masks, signal-triggered debug toggling, and fatal-error helpers.

Important APIs, types, and functions: Implements `xlog_open`, `xlog_stderr`, `xlog_syslog`, `xlog_config`, `xlog_sconfig`, `xlog_enabled`, `xlog_backend`, `xlog`, `xlog_warn`, `xlog_err`, and `xlog_errno`. Internal state includes `log_stderr`, `log_syslog`, `logging`, `logmask`, `log_name`, and `log_pid`. `debugnames` maps strings such as `general`, `call`, `auth`, `parse`, and `all` to debug masks.

Control flow: `xlog_open` initializes syslog identity, captures program name/pid, and installs SIGUSR1/SIGUSR2 handlers. Config functions update masks and enable debug logging. `xlog_backend` filters non-severity debug records unless enabled, writes to syslog at severity-derived priorities, writes to stderr with optional timestamp format, and exits on `L_FATAL`. Wrapper functions package variadic arguments and choose severity.

State and persistence: Logging state is process-global and mutable at runtime via config functions and signals. No disk persistence beyond syslog/stderr destinations. `export_errno` is set for selected error/general logs and exported through `xlog.h`.

Dependencies and integration points: Used by rpcbind daemon and helpers for debug/error reporting. It depends on POSIX signal APIs, syslog, stdio, and `va_list` handling.

Risks: Signal handlers call `xlog`, which is not async-signal-safe because it may use syslog, stdio, and allocation-like library internals. `xlog_backend` uses one `va_list` for syslog and a copied one for stderr, which is correct only because copying occurs before consuming. Facility/severity exact `switch` cases mean combined flags may fall to default behavior.

Test signals: Unit-style tests can validate mask enable/disable behavior, string facility parsing, syslog/stderr toggles, warning/error/fatal routing, and that `xlog_enabled` tracks runtime configuration. Signal behavior is best covered by integration tests because of process exit and handler side effects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/xlog.c -->
