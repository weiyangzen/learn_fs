# sources/sync-backup/casync/src/log.c

Purpose: implements the small process-wide logging layer used by casync tools and tests. Messages go to `stderr` with a priority prefix and optional errno text.

Important APIs/types/functions: `set_log_level`, `set_log_level_from_string`, `log_info_errno`, `log_error_errno`, and `log_debug_errno`. `level_from_string` accepts emergency through debug plus numeric levels; `get_log_level` lazily reads `$SYSTEMD_LOG_LEVEL`.

Control flow/state: `log_max_level` is a static global initialized to `-1`. Each public logger funnels through `log_fullv`, which suppresses messages above the current max level, appends `strerror(abs(error))` when `error` is nonzero, and returns negative errno for error-carrying calls.

Dependencies/integration: uses syslog priority constants, stdio varargs, and `isempty` from `util.h`. `log.h` wraps it in ergonomic macros used by test helpers, notify-wait, and utility failures.

Risks/test signals: global log level is not synchronized, so concurrent reconfiguration would race. Environment parsing accepts numeric values that may not map to known syslog severities. Tests mostly exercise this indirectly through failing `assert_se` and helper diagnostics.

Source research group: `subset-b-009122`.
