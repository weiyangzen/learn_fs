# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/InfoLogLevel.java research

## Purpose

`InfoLogLevel` is the Java representation of RocksDB's native logging levels. It is used by `Options`, `DBOptions`, and `Logger` to configure filtering and to decode native log-level bytes back into Java constants.

## Important APIs and types

The constants are `DEBUG_LEVEL`, `INFO_LEVEL`, `WARN_LEVEL`, `ERROR_LEVEL`, `FATAL_LEVEL`, `HEADER_LEVEL`, and `NUM_INFO_LOG_LEVELS`. `getValue()` returns the native byte. `getInfoLogLevel(byte)` performs a linear lookup and throws `IllegalArgumentException` for unknown bytes.

## Control flow

Setter code passes `getValue()` to JNI. Getter code retrieves a byte from native state and calls `getInfoLogLevel()`. Java callback loggers receive decoded levels when native code invokes the Java logging callback.

## State and persistence behavior

The enum stores immutable byte constants. The selected level is held in native options or logger state and can affect which log records are emitted to persistent LOG files or Java logging sinks.

## Dependencies and integration points

It integrates directly with `Logger`, `LoggerInterface`, `Options.setInfoLogLevel()`, and native RocksDB logging. The byte mapping is a JNI contract.

## Risks and test signals

Risks are enum drift and invalid native bytes causing exceptions in getter paths or logger callbacks. Tests should verify all byte round-trips, invalid-byte rejection, and that `Options` and custom `Logger` instances observe level changes.
