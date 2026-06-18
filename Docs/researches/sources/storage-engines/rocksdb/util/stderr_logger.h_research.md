# sources/storage-engines/rocksdb/util/stderr_logger.h

## Purpose

Declares a `Logger` subclass that prints logs to stderr and can attach an optional per-line prefix after RocksDB's time/thread context.

## APIs, control flow, and state

`StderrLogger` has constructors for only log level or log level plus string prefix. The prefixed constructor duplicates the prefix into `log_prefix` and records its length. The class overrides `Logv(const char*, va_list)` and brings base overloads into scope with `using Logger::Logv`.

## Dependencies and integration

It depends on `rocksdb/env.h`, stdarg, and stdio. The type is drop-in for RocksDB components that accept a `Logger*` or shared logger object.

## Risks and test signals

No tests in this subset instantiate it. The main ownership risk is that `log_prefix` is a raw duplicated C string, so constructor/destructor behavior in `stderr_logger.cc` must stay paired. The class is non-copy-disabled only by base-class behavior, not explicitly in this header.
