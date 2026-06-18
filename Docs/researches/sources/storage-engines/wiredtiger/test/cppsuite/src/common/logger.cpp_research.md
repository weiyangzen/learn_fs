# sources/storage-engines/wiredtiger/test/cppsuite/src/common/logger.cpp

Purpose: Implements synchronized cppsuite logging with timestamp, thread id, and log level.

Important APIs/types/functions: `get_time` formats UTC-like timestamp strings with nanosecond suffix from `high_resolution_clock`. `logger::log_msg` checks `trace_level`, validates level bounds, builds a message with TID and level, locks a static mutex, and writes errors to stderr and other levels to stdout.

Control flow: logging is skipped when requested level is above current `trace_level`. Message construction happens before acquiring the output lock; actual stream writes are serialized.

State and persistence: mutable static `logger::trace_level` and `logger::include_date`; no file persistence.

Dependencies/integration: depends on `test_util`, C++ streams, thread ids, and `LOG_LEVELS`; used across the harness for diagnostics.

Risks and test signals: per-line locking can be expensive at trace level. Timestamp uses localtime for calendar fields but appends `Z`, which can mislead interpretation. Assertions catch invalid trace levels and time formatting failures.
