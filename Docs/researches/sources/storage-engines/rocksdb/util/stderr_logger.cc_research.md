# sources/storage-engines/rocksdb/util/stderr_logger.cc

## Purpose

Implements `StderrLogger`, a debugging logger that writes formatted log lines directly to stderr with timestamp and thread context.

## APIs, control flow, and state

The destructor frees an optional duplicated prefix. `Logv` retrieves the current RocksDB thread id, reads wall-clock time, formats a fixed context prefix, computes the formatted log-message length using `va_copy` and `vsnprintf`, allocates a buffer, writes context plus optional user prefix, writes the message suffix, and emits it to `stderr` with a newline.

## Dependencies and integration

It depends on `Env::Default()->GetThreadID`, `port::GetTimeOfDay`, `port::LocalTimeR`, and `port/malloc.h`. It integrates wherever a `Logger` implementation is accepted, especially fast local debugging paths.

## Risks and test signals

There are no local tests. Risks include manual prefix memory management, reliance on the context buffer size estimate, `snprintf` return values, and thread-safety through shared stderr rather than internal serialization. The implementation handles missing prefix by substituting an empty string.
