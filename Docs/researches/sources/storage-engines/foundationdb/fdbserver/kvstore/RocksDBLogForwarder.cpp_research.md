# sources/storage-engines/foundationdb/fdbserver/kvstore/RocksDBLogForwarder.cpp

## Purpose
This file adapts RocksDB info logging into FoundationDB `TraceEvent`s. It accepts RocksDB log callbacks from arbitrary RocksDB threads, buffers non-main-thread records, and periodically drains them on the Flow event-loop thread where trace logging is safe.

## Important APIs, Types, And Functions
`getSeverityFromLogLevel` maps RocksDB `InfoLogLevel` values to FoundationDB severities. `details::logTraceEvent` emits a `RocksDBLogRecord` trace with receive time, RocksDB thread id, and parsed key/value fields. `rocksDBPeriodicallyLogger` is a Flow actor that calls `RocksDBLogger::consume` every 0.1 seconds. `RocksDBLogger::inject` either logs immediately on the main thread or pushes into a mutex-protected vector. `consume` swaps and drains buffered records. `RocksDBLogForwarder::Logv` formats RocksDB varargs into text and injects a record, adding a backtrace for error-level events.

## Control Flow
The `RocksDBLogForwarder` constructor starts with a `RocksDBLogger` member whose constructor captures the current thread id and starts the periodic drain actor. RocksDB calls either `Logv(format, ap)` or `Logv(level, format, ap)`. The implementation clamps severity to at most warning for most levels, formats into a fixed 1024-byte buffer, builds a `RocksDBLogRecord`, and gives it to `RocksDBLogger`. If the callback is on the main thread, the event is emitted directly and any queued background-thread logs are consumed. Otherwise, the record is queued until the periodic actor drains it.

## State And Persistence Behavior
All state is in-process: the logger's main thread id, mutex, pending vector, and periodic actor future. There is no disk persistence. The destructor emits a stop trace but does not explicitly drain or cancel in this file; the `Future` member lifecycle determines actor cancellation.

## Dependencies And Integration Points
The file is compiled under `WITH_ROCKSDB`. It depends on RocksDB `Logger`, Flow `TraceEvent`, Flow actors, `now()`, `platform::get_backtrace`, and thread ids. It can be installed into RocksDB options as an `info_log` implementation by storage engines that want RocksDB logs in FDB traces.

## Risks
Trace events are unsafe from arbitrary RocksDB background threads, so the buffering distinction is essential. If `RocksDBLogger` is constructed off the actual Flow event-loop thread, the "main thread" fast path may be wrong. The fixed 1024-byte `vsnprintf` buffer truncates long RocksDB messages. The TODO notes that log parsing is currently just one `"Text"` field. The severity clamp uses `std::min(..., SevWarn)`, so RocksDB debug/info become no more verbose than warning depending on severity ordering; this was intentionally restricted to reduce simulation failures but may distort severity. Buffered records can grow if the event loop is stalled.

## Test Signals
Tests should verify severity mapping, immediate logging on the owning thread, queued logging from a background thread, periodic draining, error backtrace attachment, truncation behavior for long messages, destructor behavior with queued records, and simulation behavior under high RocksDB log volume.
