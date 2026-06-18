# File Research: sources/virtualization/spdk/lib/log/log.c

Implements SPDK's base logging backend: log levels, stderr/syslog routing, optional custom callbacks, timestamp generation, file logging, and hex dumping.

Key entry points:
- `spdk_log_set_level()` / `spdk_log_get_level()` configure syslog emission level.
- `spdk_log_set_print_level()` / `spdk_log_get_print_level()` configure stderr emission level.
- `spdk_log_open()`, `spdk_log_open_ext()`, and `spdk_log_close()` configure syslog or caller-provided log callbacks/open/close hooks.
- `spdk_log_enable_timestamps()` toggles timestamp prefixes.
- `spdk_log()` and `spdk_vlog()` are the primary variadic logging paths.
- `spdk_flog()` and `spdk_vflog()` write formatted log records to an arbitrary `FILE`.
- `spdk_log_dump()` prints a hex/ascii dump of a memory buffer.

Core mechanics:
- If a custom `g_log_opts.log` callback is installed, `spdk_vlog()` delegates immediately and bypasses built-in filtering and output formatting.
- Built-in logging filters independently against `g_spdk_log_print_level` for stderr and `g_spdk_log_level` for syslog.
- `spdk_log_to_syslog_level()` maps SPDK levels to syslog severities and drops `SPDK_LOG_DISABLED`.
- Messages are formatted into a 1024-byte stack buffer first; longer output attempts `vasprintf()` and falls back to truncated stack output on allocation failure.
- Timestamp prefixes use `CLOCK_REALTIME`, local time, and microsecond precision unless disabled.
- File/line/function metadata is included when `file` is non-null; otherwise the message is written without source metadata.
- `fdump()` emits 16-byte rows with offsets, hex bytes, and printable ASCII.

Important invariants:
- Log level setters assert the level is between `SPDK_LOG_DISABLED` and `SPDK_LOG_DEBUG`.
- `spdk_log_close()` clears the global options after running any close hook.
- `spdk_vflog()` always flushes its target file.
- The static `spdk_level_names[]` array relies on enum values matching its indexed entries.

Filesystem/block relevance:
- This file supplies diagnostics for all SPDK modules, including block-device and logical-volume code. It is not storage logic itself, but it is essential for operational debugging.

Notable risks:
- `localtime()` is not thread-safe on all platforms; concurrent logging can race on the returned static state.
- A custom log callback receives the original `va_list`; callback implementations must consume it correctly because built-in formatting will not run.
- `spdk_vlog()` uses `rc > MAX_TMPBUF` rather than `rc >= MAX_TMPBUF` when deciding to allocate an expanded buffer, so exactly boundary-sized formatted output may remain truncated by `vsnprintf()` semantics.
