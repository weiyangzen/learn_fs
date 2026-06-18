# sources/user-network-fs/nfs-ganesha/src/include/log.h

## Purpose

`log.h` is Ganesha's main logging interface. It declares initialization, component log-level control, cleanup/fatal handling, log facilities, DBus integration, backtrace helpers, rate limiting, and the macro family used throughout the server.

## Important APIs, Types, and Functions

Core functions include `init_logging`, `SetNamePgm`, `SetNameHost`, `SetNameFunction`, `SetClientIP`, `DisplayLogComponentLevel`, `SetComponentLogLevel`, `read_log_config`, and `LogMallocFailure`. Facility APIs create, enable, disable, set destination, and set level for named sinks. Global state includes `component_log_level`, `conditional_component_log_level`, `cond_log_match_policy`, `conditional_logging_configured`, and `LogComponents`. Logging macros cover fatal, major, critical, warning, event, info, debug, mid-debug, full-debug, alternate-component logging, opaque/byte formatting, warn-once, and rate-limited event/warn messages.

## Control Flow

Most macros first call `isLevel` to avoid formatting work when disabled, then call `DisplayLogComponentLevel` with source location and function. Conditional logging can override component levels when request context marks a conditional match. Rate-limited macros keep a static `ratelimit_state` per call site and emit missed-message counts.

## State and Persistence Behavior

Logging keeps process-wide component levels, facility state, program/host/client/function names, cleanup callbacks, and per-call-site static rate-limit state. Output persists only through configured sinks such as syslog, file, stderr/stdout, test log, or custom facilities.

## Dependencies and Integration Points

It depends on `log_common.h`, config parsing, display buffers, list helpers, `ip_utils.h`, pthreads, syslog, and optional DBus/unwind. Every subsystem integrates through component macros, making this header a high-blast-radius API.

## Risks and Test Signals

Risks include format-string mismatches, expensive macro arguments evaluated unexpectedly in custom wrappers, conditional logging races, static rate-limit contention, fatal abort behavior in tests, and facility lifetime leaks. Tests should cover level parsing, component threshold behavior, conditional request logging, file/syslog/test destinations, DBus level changes, rate-limit missed counts, backtrace calls, and compile-time printf attribute checks.
