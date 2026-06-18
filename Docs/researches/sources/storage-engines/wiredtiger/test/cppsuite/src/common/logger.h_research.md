# sources/storage-engines/wiredtiger/test/cppsuite/src/common/logger.h

Purpose: Declares log-level constants and the non-instantiable `logger` utility.

Important APIs/types/functions: defines `LOG_ERROR`, `LOG_WARN`, `LOG_INFO`, and `LOG_TRACE`; declares `get_time`; exposes static `trace_level`, `include_date`, and `log_msg`.

Control flow: callers use numeric levels to gate messages through `logger::log_msg`.

State and persistence: static configuration controls global logging behavior during a process.

Dependencies/integration: included by components, thread manager, metrics, and database code.

Risks and test signals: changing level values requires updating the implementation's `LOG_LEVELS` array. Logging is a diagnostic signal, not a validation mechanism.
