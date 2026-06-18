# sources/storage-engines/rocksdb/trace_replay/block_cache_tracer.h

## Purpose

Declares the block cache tracing API used to capture, write, read, classify, and optionally render RocksDB block cache accesses.

## Important APIs, Control Flow, And Dependencies

The header defines time constants, `BlockCacheTraceHelper`, `BlockCacheLookupContext`, `BlockCacheTraceHeader`, `BlockCacheTraceWriterImpl`, `BlockCacheHumanReadableTraceWriter`, `BlockCacheTraceReader`, `BlockCacheHumanReadableTraceReader`, and `BlockCacheTracer`. `BlockCacheLookupContext` carries table-reader caller, cache hit/insert flags, block metadata, get ID, referenced key, and snapshot state from table reader call sites to the tracer. `BlockCacheTracer` exposes `StartTrace`, `EndTrace`, `is_tracing_enabled`, `WriteBlockAccess`, and `NextGetId`.

## State, Persistence, Integration, Risks, And Test Signals

The declared persistent outputs are binary trace records through a user-provided `TraceWriter` and optional human-readable files through `WritableFile`. Integration points are table-reader call sites such as filter/dictionary/data/index/range-deletion block reads and user `Get`, `MultiGet`, iterator, compaction, prefetch, and checksum callers. The tracer uses an atomic writer pointer plus mutex for cross-thread control. Risks include lifetime ownership of writer objects, callers needing to fill lookup context consistently, and helper assumptions about referenced key and block key encodings. Tests cover the public behavior through generated trace files and decoded records.
