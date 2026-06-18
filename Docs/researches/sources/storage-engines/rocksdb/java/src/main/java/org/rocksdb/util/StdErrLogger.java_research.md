# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/util/StdErrLogger.java

## Purpose
`StdErrLogger` is a native-backed logger implementation that redirects RocksDB log messages to standard error.

## Important APIs and Types
Constructors accept `InfoLogLevel` and optional prefix. It implements `LoggerInterface` methods `setInfoLogLevel`, `infoLogLevel`, and `getLoggerType`, returning `LoggerType.STDERR_IMPLEMENTATION`.

## Control Flow, State, and Persistence
Construction creates a native stderr logger with log level and prefix. Level changes and reads dispatch to JNI. Disposal is native. Logging output goes to process stderr rather than DB log files.

## Dependencies and Integration Points
Depends on `InfoLogLevel`, `LoggerInterface`, `LoggerType`, `RocksObject`, and JNI. It integrates with DB/backup/options APIs that accept RocksDB loggers.

## Risks and Test Signals
Risks include native handle lifetime, stderr noise in embedded applications, and null-prefix handling. Backup and table tests create other logger implementations but do not directly test `StdErrLogger`.
