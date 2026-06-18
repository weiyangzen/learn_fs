# sources/storage-engines/rocksdb/logging/event_logger.h

Purpose: Header for RocksDB structured event logging and lightweight JSON assembly.

Important APIs/types/functions: `JSONWriter`, `EventLoggerStream`, `EventLogger`, `Prefix`, `Log`, `LogToBuffer`, array/object methods and stream insertion operators.

Control flow and state: `JSONWriter` is a small state machine alternating between key and value states, with special handling for arrays and arrayed objects. `EventLoggerStream` forwards insertions to the writer and emits on destruction. `EventLogger` binds either direct logger output or log-buffer output.

State and persistence behavior: no persistence by itself; generated JSON strings flow to info logs or buffers.

Dependencies and integration points: used by RocksDB subsystems that emit machine-readable operational events to LOG.

Risks: JSON string values are not escaped for quotes/backslashes, so unsafe values can produce invalid JSON. State assertions are debug-time only. Nested object/array support is limited.

Test signals: simple field-presence test exists; complex JSON state transitions are not heavily tested in this subset.
