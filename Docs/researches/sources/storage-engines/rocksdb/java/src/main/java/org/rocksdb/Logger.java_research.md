# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/Logger.java research

## Purpose

`Logger` is the abstract Java callback logger for RocksDB. It lets native RocksDB send log records into Java logging frameworks instead of only writing filesystem LOG files.

## Important APIs and types

The active constructor accepts `InfoLogLevel`. Deprecated constructors derive the level from `Options` or `DBOptions`. `initializeNative(...)` creates a native callback logger from one log-level argument. `setInfoLogLevel()`, `infoLogLevel()`, `getNativeHandle()`, and `getLoggerType()` implement `LoggerInterface`. Subclasses implement `protected abstract void log(InfoLogLevel, String)`.

## Control flow

Construction goes through `RocksCallbackObject`, then `initializeNative()` calls native `newLogger`. Native RocksDB checks the configured level and invokes the Java `log` callback for accepted messages. Disposal uses a specialized native path because the underlying C++ object is held through `std::shared_ptr`.

## State and persistence behavior

The object owns a native callback handle and has no durable state. It can redirect persistent logging away from DB LOG files depending on options. Java subclasses may persist records through their chosen logging backend.

## Dependencies and integration points

It integrates with `Options.setLogger(LoggerInterface)`, `InfoLogLevel`, `LoggerType.JAVA_IMPLEMENTATION`, and the `RocksCallbackObject` lifecycle. It crosses JNI on every emitted log message.

## Risks and test signals

The class warns about production overhead from native-to-Java transitions and native allocations for verbose levels. Risks include callback exceptions, premature disposal while native options still reference the logger, and incorrect level filtering. Tests should cover custom logger callbacks, level round-trips, disposal, and `Options.setLogger()` integration.
