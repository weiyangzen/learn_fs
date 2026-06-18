# sources/storage-engines/foundationdb/fdbserver/kvstore/RocksDBLogForwarder.h

## Purpose
This header declares the RocksDB-to-FoundationDB log forwarding adapter. It defines the record structure and logger classes needed to convert `rocksdb::Logger` callbacks into Flow trace events safely.

## Important APIs, Types, And Functions
`details::RocksDBLogRecord` stores one transformed RocksDB log line: receive time, severity, UID, source thread id, and key/value fields. `details::RocksDBLogger` owns buffered records, exposes `inject(RocksDBLogRecord&&)` and `consume()`, and maintains a periodic drain actor. `RocksDBLogForwarder` derives from `rocksdb::Logger`, stores an FDB UID and `RocksDBLogger`, and overrides both `Logv` overloads.

## Control Flow
The header only declares behavior. Its comments document the main constraint: `RocksDBLogger` must run in a thread that can generate `TraceEvent`s. RocksDB calls `Logv`; the implementation in the `.cpp` handles formatting, severity mapping, buffering, and trace emission.

## State And Persistence Behavior
The declared classes store only process-local logging state. `RocksDBLogger` uses a mutex-protected vector because RocksDB logging can occur from multiple threads. No state is persisted.

## Dependencies And Integration Points
The declarations are under `WITH_ROCKSDB` and depend on `rocksdb/env.h`, Flow generic actors, deterministic random headers indirectly used by Flow code, `Trace.h`, `UID`, `Severity`, `Future<Void>`, and C++ threading/mutex/vector/string support. The top-level `RocksDBLogForwarder` can be passed to RocksDB options as a logger.

## Risks
The thread-affinity requirement is easy to violate because the constructor captures a main thread id implicitly. Header consumers must compile only with RocksDB support. The inheritance from `rocksdb::Logger` means RocksDB controls callback lifetime, so the object must outlive any DB using it.

## Test Signals
Compile tests should cover `WITH_ROCKSDB` builds and include this header independently. Behavioral tests belong to the `.cpp`: multi-thread inject, consume, `Logv` formatting, and lifetime under RocksDB DB open/close.
