# sources/object-store/openstack-swift/swift/common/utils/logs.py

## Purpose
This module centralizes Swift logging behavior for daemons, WSGI servers, request access logs, and stdio capture. It adapts Python logging for eventlet, syslog, Swift transaction context, backend access-log formatting, optional anonymization, and custom operator handlers. It is a shared utility, so changes here affect most Swift services.

## Important APIs, Types, and Functions
- `logging_monkey_patch()` replaces `logging._lock`, registers Swift's `NOTICE` level, maps syslog notice priority, and disables thread logging to avoid deadlocks under monkey patching.
- `PipeMutex` implements a recursive green-thread-aware mutex using an OS pipe so real threads and eventlet greenthreads can coordinate on logging handlers. It disables eventlet's multiple-reader guard.
- `NoopMutex` is the default syslog handler lock for UDP/UDS logging and deliberately avoids serialization while still disabling eventlet multiple-reader detection.
- `ThreadSafeSysLogHandler.createLock()` selects `NoopMutex` unless `SWIFT_NOOP_LOGGING_MUTEX` is false-like, otherwise uses `PipeMutex`.
- `SwiftLogAdapter` wraps loggers with server name, prefix, thread-local `txn_id` and `client_ip`, a `notice()` method, and exception normalization for common socket, HTTP, disk, and timeout failures.
- `SwiftLogFormatter` injects server identity, appends transaction and client IP context when absent from messages, flattens newlines as `#012`, and truncates long lines using middle elision.
- `LoggerFileObject` redirects stdout/stderr into logging while guarding against recursive logging-handler failures.
- `get_swift_logger()` constructs/replaces syslog and optional console handlers from config keys such as `log_facility`, `log_level`, `log_address`, `log_udp_host`, `log_max_line_length`, and `log_custom_handlers`.
- `capture_stdio()` replaces uncaught exception handling and redirects stdio to `LoggerFileObject`, except fds already used by configured console logging.
- `StrAnonymizer`, `StrFormatTime`, `LogStringFormatter`, `get_log_line()`, and `get_policy_index()` build backend access log lines with formatted time, request path parts, anonymization, policy index extraction, and safe default fields.

## Control Flow and Behavior
Logger creation removes any previous handler stored in `get_swift_logger.handler4logger` before adding the new configured syslog handler, so the last call controls handler configuration for a logger route. Console logging is similarly tracked in `console_handler4logger`; once a console handler map exists, later calls refresh console handlers even if `log_to_console` is false. `SwiftLogAdapter.process()` injects extra logging fields on every log call, while `exception()` decides whether to log a compact operational message or a full traceback depending on exception type and errno.

Access log construction in `get_log_line()` derives path components via `split_path`, wraps sensitive fields in `StrAnonymizer`, and formats through `LogStringFormatter(default='-')`. The anonymizer hashes only when a non-empty value exists and uses Swift's md5 helper with `usedforsecurity=False` for md5.

## State and Persistence
Persistent external state is limited to process logging configuration, class-level thread/greenthread local fields, handler maps attached to `get_swift_logger`, environment-variable configuration for logging mutex behavior, and stdio replacement in `capture_stdio()`. `PipeMutex` owns OS pipe fds and closes them in `close()` and `__del__()` to avoid test-suite fd leaks.

## Dependencies and Integration Points
The module depends on eventlet primitives from `swift.common.concurrency`, Swift config parsing helpers, Swift exception types, Python `logging`/`SysLogHandler`, and request objects with WebOb-like attributes. It is integrated by `swift.common.wsgi`, daemon startup, backend servers, proxy logging middleware, and custom handler hooks named by `log_custom_handlers`.

## Risks and Edge Cases
- Logging configuration is global by route; repeated `get_swift_logger()` calls replace handlers and can surprise tests or embedded apps.
- `capture_stdio()` mutates `sys.stdout`, `sys.stderr`, and `sys.excepthook`, which is process-wide.
- `NoopMutex` is safe only under Swift's assumptions about UDP/UDS syslog message boundaries; switching transports or handlers can alter concurrency safety.
- `StrAnonymizer` encodes data and salt as latin-1, so unexpected non-latin-1 values can fail.
- Access-log format strings are operator-controlled and may raise if they reference invalid `StrFormatTime` directives.
- Recursive logging from syslog failures is explicitly mitigated, but handler errors still risk log loss.

## Test Signals
Useful tests should cover logger reconfiguration idempotency, NOTICE level mapping, eventlet/thread mutex recursion and close behavior, exception message normalization by errno and timeout class, stdio recursion guards, anonymized and quoted access-log formatting, policy-index byte/string handling, custom handler import failures, and max-line truncation.
