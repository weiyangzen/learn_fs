# sources/storage-engines/rocksdb/logging/logging.h

Purpose: Macro layer for RocksDB logging with file/line prefixes and log levels.

Important APIs/types/functions: `ROCKS_LOG_PREPEND_FILE_LINE`, `RocksLogShorterFileName`, `ROCKS_LOG_HEADER`, `ROCKS_LOG_AT_LEVEL`, level macros, buffer macros, `ROCKS_LOG_DETAILS`.

Control flow and state: macros expand to generic `Log`/`LogToBuffer` calls, adding shortened file name and source line for non-header logs. Header logs intentionally omit file/line metadata. Details logging is compiled as an empty statement by default.

State and persistence behavior: no state; persistence depends on target logger/buffer.

Dependencies and integration points: included by `.cc` files only to avoid namespace pollution; used broadly across RocksDB internals.

Risks: macro formatting can evaluate arguments according to varargs rules and lacks type safety. `RocksLogShorterFileName` depends on this header’s path length constant. Empty details macro can hide side effects if arguments are ever added there.

Test signals: indirectly covered by logger tests that count output lines and header behavior.
