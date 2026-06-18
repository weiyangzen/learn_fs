<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/log/log_functions.c -->
# sources/user-network-fs/nfs-ganesha/src/log/log_functions.c

## Purpose
This is the central logging implementation for NFS-Ganesha. It owns log facility registration, active/default logger selection, log message formatting, component and conditional component log levels, file/syslog/stream output, in-process log rotation, crash backtrace emission, DBus log control surfaces, and parsing/committing of the `LOG` configuration block.

## Important APIs, Types, and Functions
Key global state includes `log_rwlock`, `cond_log_rwlock`, `log_rotate_rwlock`, `last_rotation_time`, `logfields`, `log_rotate_limits`, `facility_list`, `active_facility_list`, `default_facility`, `max_headers`, `component_log_level`, `conditional_component_log_level`, `default_log_level`, `original_log_level`, `rpc_debug_flags`, `global_export_id_list`, `global_client_ip_list`, `conditional_logging_configured`, and `cond_log_match_policy`. Thread-local logging context is carried in `thread_name`, `log_buffer`, and `clientip`.

Important structures are `struct logfields` for header/date/component display choices, `struct log_facility` for an output sink, `struct logger_config` for staged config parsing, `struct facility_config` for a pending facility block, and `struct conditional_config` for conditional log levels. `tabLogLevel`, `ConditionalLogPolicy`, `default_log_levels`, `default_conditional_log_levels`, and `LogComponents` map enum values to strings, short names, and syslog levels.

Public/externally important functions include `init_logging`, `Cleanup`, `RegisterCleanup`, `Fatal`, `ReturnLevelAscii`, `ReturnLevelInt`, `ReturnMatchPolicyAscii`, `SetNamePgm`, `SetNameHost`, `SetNameFunction`, `SetClientIP`, `SetComponentLogLevel`, `SetConditionalComponentLogLevel`, `DisplayLogComponentLevel`, `display_log_component_level`, `LogMallocFailure`, `rpc_warnx`, `read_log_config`, `gsh_log_backtrace`, `_ratelimit`, `conditional_logging_export_match`, and `conditional_logging_client_match`. Facility management is exposed through `create_log_facility`, `release_log_facility`, `enable_log_facility`, `disable_log_facility`, `set_log_destination`, and `set_log_level`; `set_default_log_facility` is internal.

## Control Flow
`init_logging()` initializes locks and lists, builds the default constant header fragment, creates `STDERR`, `STDOUT`, and `SYSLOG` facilities, chooses a default facility based on `-L`/`log_path`, optionally creates a `FILE` facility, and applies the startup debug level. If enriched libunwind is enabled, it also starts a watchdog thread that aborts if crash handling appears stuck.

Message emission enters through `DisplayLogComponentLevel()` or `display_log_component_level()`. The latter writes a timestamp/header prefix with `display_log_header()`, adds per-message component context through `display_log_component()`, appends the formatted user message, then takes `log_rwlock` for reading and sends the buffer to every active facility whose `lf_max_level` allows the message. Facility callbacks can output only the body, component-prefixed body, or full header depending on `lf_headers`. Fatal-level messages call `Fatal()` after dispatch, which logs a backtrace and exits.

Output callbacks are specialized. `log_to_syslog()` lazily calls `openlog()` and writes the component-formatted string at the syslog priority mapped from the Ganesha log level. `log_to_stream()` appends a temporary newline, chooses the substring requested by the header mode, writes/flushed a `FILE *`, then restores the buffer. `log_to_file()` opens the destination on each write with append/create, writes the full buffer plus newline, checks rotation, closes, and reports write/open/close failures to stderr.

Log rotation is controlled by `log_rotate_limits`. `should_rotate()` checks configured size and elapsed monotonic time. `rotate_if_should()` rechecks under `log_rotate_rwlock`, renames the active path to `<path>.old`, and updates `last_rotation_time` after successful rename.

Config parsing is staged. `read_log_config()` calls the config parser with `logging_param`. Nested init/commit handlers allocate temporary `logfields`, component-level arrays, facility configs, conditional-level arrays, and rotate limits. `log_conf_commit()` creates or updates facilities first, releases failed new facilities, then swaps validated global `logfields` and `log_rotate_limits`, applies default/component levels through `apply_logger_config_levels()`, updates conditional match policy, UTC timestamp selection, and nTI-RPC debug flags. On validation/resource errors, temporary objects are freed instead of becoming active.

Conditional logging input can arrive from config (`Conditional { Exports; Clients; ... }`) or DBus. Config adders call `add_export_id()` and `add_client()` and set `conditional_logging_configured` on success. Runtime match helpers delegate to `is_export_id_match()` and `client_match()`. DBus methods enable/disable exports and clients, list configured entries, and change/show match policy.

Crash backtraces choose libunwind if compiled, optionally followed by enriched `addr2line` output using `/proc/self/maps`. Otherwise `backtrace()`/`backtrace_symbols_fd()` are used. Backtrace code tries to write directly to an active file facility when available to reduce reliance on regular logging during failure handling.

## State and Persistence Behavior
Most logging state is in process memory and protected by read/write locks. Facility names and file paths are heap-owned; file facility paths are duplicated and freed on release/destination replacement. Configured `logfields` and rotate limits replace previous heap-backed objects after successful commit. Component level arrays are global pointers, but active component levels are ultimately copied into `component_log_level` and `conditional_component_log_level`; temporary arrays are freed after commit.

Output persistence is external: file logs append to configured paths, syslog persists through the platform logger, and stream logs go to process stdout/stderr. Rotation persists by renaming one generation to `.old`; there is no multi-generation retention in this file. `disp_utc_timestamp`, `date_time_fmt`, `const_log_str`, and the static log index counter affect formatting but are not persisted across process restart.

Thread context is transient and thread-local. `SetNameFunction()` resets `clientip`; callers must ensure the pointer passed to `SetClientIP()` remains valid for the duration of the thread. Conditional export/client lists persist only in memory unless specified in config and reread on restart.

## Dependencies and Integration Points
The file integrates with `log.h`, `log_common.h`, `display_buffer` helpers, Ganesha lists, memory wrappers, config parsing, core server state (`nfs_core.h`, `op_ctx`, `nfs_param` elsewhere), nTI-RPC debug control (`ntirpc_pp`, `tirpc_control`), SAL export/client helper functions, optional DBus (`gsh_dbus.h`), optional libunwind, optional fridgethr watchdog support, libc syslog, POSIX file APIs, and platform time APIs.

DBus integration exports `org.ganesha.nfsd.log.component` and, when conditional logging is enabled in the build, `org.ganesha.nfsd.log.conditional`. Config integration exposes the unique `LOG` block with nested `Facility`, `Format`, `Components`, `Rotate`, and `Conditional` blocks. Logging also feeds TI-RPC through `rpc_warnx()` and maps `COMPONENT_TIRPC` levels to `ntirpc_pp.debug_flags`.

## Risks and Edge Cases
The logging file deliberately undefines tracing variants of `PTHREAD_RWLOCK_*` to avoid recursive logging, but any future lock/log interaction inside this file can still deadlock if it calls regular logging while holding incompatible locks. `DisplayLogComponentLevel()` holds `log_rwlock` while invoking facility callbacks; callbacks that block on slow disks, stderr, syslog, or close/write stalls delay all concurrent logging.

`log_to_file()` opens and closes the file per message, which avoids shared descriptor lifecycle issues but adds per-log syscall overhead. Rotation is single-generation and races are only partially mitigated; writes that already opened the old path can continue around rename. `rotate_if_should()` opens the current path read-only to recheck size/time, so failure to open suppresses rotation.

`display_timeval()` and `display_timespec()` call `display_printf(dspbuf, tbuf, tv->tv_usec/ts->tv_nsec)` when user-controlled date/time formats select microsecond output. Because `tbuf` is used as a format string, only trusted/admin-controlled format strings should reach `user_date_fmt`/`user_time_fmt`; malformed `%` sequences can behave like format strings.

Conditional DBus handlers generally return a success boolean even when `errormsg` reports an argument or validation failure, so clients must inspect the status reply text/fields rather than only method return. `dbus_conditional_log_export_disable()` calls `gsh_free(&export_entry->export_id_glist)`, which is suspicious because the list member address may not be the allocation base unless `struct export_id_list` embeds it at offset zero.

`get_code_location()` builds an `addr2line` shell command with `popen()`, which is not signal-safe and is intentionally best-effort under the crash watchdog. Enriched backtraces depend on Linux `/proc/self/maps`; portability is limited. `strip_new_line_from_string_end()` assumes a non-empty string.

The default/component level logic uses `NB_LOG_LEVEL` as a sentinel; incorrect initialization of arrays would make normal log levels look unset. Compile-time `CT_ASSERT`s protect enum-array size drift for the main component tables. `SetNamePgm()` and `SetNameHost()` call fatal logging on truncation, which can terminate during early startup.

## Test Signals
Relevant signals include unit or integration tests for `ReturnLevelAscii()` accepting full, shortened, and `NIV_`-less names; config tests covering `LOG` block commit/rollback, `Facility` create/update/default/active states, `Format` validation for user-defined date/time formats, `Components { ALL }` precedence, `Default_Log_Level`, `Rotate`, and `Conditional` lists; DBus tests for component and conditional property get/set plus export/client enable/disable/list/match policy methods; and runtime tests that verify fatal logs emit backtraces.

Operational tests should verify simultaneous logging from many threads, slow or missing log files, invalid file destinations, rotation by size/time, syslog open-on-first-use, stdout/stderr header modes, UTC/local timestamp selection, nTI-RPC debug flag updates when `COMPONENT_TIRPC` changes, and conditional matching by export and client.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/log/log_functions.c -->
