# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LoggerInterface.java research

## Purpose

`LoggerInterface` defines the minimum Java contract for objects that can be installed as RocksDB loggers. It abstracts both Java callback loggers and native/stderr-backed logger implementations.

## Important APIs and types

The interface requires `setInfoLogLevel(InfoLogLevel)`, `infoLogLevel()`, `getNativeHandle()`, and `getLoggerType()`. These methods provide both configuration and enough identity for `Options.setLogger(...)` to pass the correct native handle and logger-kind byte over JNI.

## Control flow

Implementations perform the actual work. `Options` consumes the interface, calls `getNativeHandle()` and `getLoggerType().getValue()`, and native RocksDB adopts or references the logger according to the implementation type.

## State and persistence behavior

The interface has no state. Implementations may own native handles or Java callback state. Log persistence depends on the concrete logger.

## Dependencies and integration points

It depends on `InfoLogLevel` and `LoggerType`. The main implementation in this subset is `Logger`; other native logger wrappers can implement the same interface.

## Risks and test signals

Implementations must return a native handle whose lifetime covers native use. Tests should verify that every implementation reports the correct `LoggerType`, supports level changes, and works when installed in `Options`.
