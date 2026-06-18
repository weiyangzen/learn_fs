# sources/storage-engines/rocksdb/logging/log_buffer.h

Purpose: Declaration of `LogBuffer`, a temporary buffer of timestamped log entries for delayed flushing.

Important APIs/types/functions: `LogBuffer`, `AddLogToBuffer`, `IsEmpty`, `FlushBufferToLog`, `kDefaultMaxLogSize`, `BufferedLog`, free `LogToBuffer` overloads.

Control flow and state: stores log level, target logger, arena allocator, and vector of `BufferedLog*`. Callers append formatted records and later flush them to the logger.

State and persistence behavior: in-memory until `FlushBufferToLog`; persisted only after target logger writes.

Dependencies and integration points: used by logging macros and event logger buffering to avoid immediate logging inside sensitive sections.

Risks: no ownership of `info_log_`; caller must keep logger alive. `IsEmpty` returns `size_t` rather than `bool`, despite semantic name. Buffer memory grows until object destruction.

Test signals: behavior is exercised indirectly by log-buffer users.
