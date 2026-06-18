# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/LoggerType.java research

## Purpose

`LoggerType` is an internal enum used to tell JNI what kind of logger handle is being passed. It distinguishes Java callback loggers from native stderr loggers.

## Important APIs and types

The constants are `JAVA_IMPLEMENTATION` and `STDERR_IMPLEMENTATION`. `getValue()` is package-private. `getLoggerType(byte)` decodes native bytes and throws `IllegalArgumentException` on unknown values.

## Control flow

`LoggerInterface` implementations report a type. `Options.setLogger()` passes the type byte with the native handle, and native code chooses the correct adapter or ownership behavior.

## State and persistence behavior

The enum stores only immutable bytes. Logger type affects runtime logging routing, not DB persistence by itself.

## Dependencies and integration points

It is used by `Logger`, `LoggerInterface`, and options JNI. The byte values must match native RocksJava expectations.

## Risks and test signals

Byte drift or wrong implementation reporting can make native code treat a handle as the wrong logger kind. Tests should cover byte decode, invalid-byte failure, and setting both Java and stderr logger implementations when available.
