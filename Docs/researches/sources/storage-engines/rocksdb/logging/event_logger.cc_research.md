# sources/storage-engines/rocksdb/logging/event_logger.cc

Purpose: Implementation of structured event logging to info logs or deferred log buffers.

Important APIs/types/functions: `EventLoggerStream` constructors/destructor, `EventLogger::Log`, static `Log`, and `LogToBuffer`.

Control flow and state: an `EventLoggerStream` lazily creates a `JSONWriter` on first insertion and adds `time_micros`. On destruction it closes the JSON object and either writes prefixed JSON to a `Logger`, writes to `LogBuffer`, or prints to stdout under compile-time flag. Static helpers prepend `EVENT_LOG_v1`.

State and persistence behavior: stream owns its `JSONWriter` until destructor. Output persists only through the target logger or buffered log flush.

Dependencies and integration points: generic `Log`, `LogToBuffer`, `LogBuffer`, chrono system clock, and optional `ROCKSDB_PRINT_EVENTS_TO_STDOUT`.

Risks: destructor-driven emission means partially constructed streams still log at scope exit. JSON escaping is minimal because `JSONWriter` writes raw strings in quotes. The stream manually owns `JSONWriter` via raw pointer.

Test signals: `event_logger_test.cc` verifies key fields in emitted output.
