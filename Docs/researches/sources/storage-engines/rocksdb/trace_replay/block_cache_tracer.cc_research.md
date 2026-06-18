# sources/storage-engines/rocksdb/trace_replay/block_cache_tracer.cc

## Purpose

Implements block cache trace helper logic, binary block cache trace writer/reader, CSV-like human-readable block cache trace writer/reader, and the thread-safe `BlockCacheTracer` controller used by RocksDB table/cache code.

## Important APIs, Control Flow, And Dependencies

`ShouldTrace` spatially downsamples by hashing the block key modulo `sampling_frequency`, preserving full history for sampled blocks. `BlockCacheTraceHelper` classifies user/get/multiget accesses, computes row keys, extracts table IDs and sequence numbers from referenced internal keys, and decodes the last varint64 in a block key as file offset. `BlockCacheTraceWriterImpl::WriteBlockAccess` encodes a `Trace` payload containing block key, size, CF id/name, level, SST number, caller, cache-hit flags, and conditional get/data-block fields before calling `TracerHelper::EncodeTrace`. The reader performs the inverse with detailed `Incomplete` errors. Human-readable writer/reader serialize and reconstruct 21 comma-separated fields for offline analysis.

## State, Persistence, Integration, Risks, And Test Signals

`BlockCacheTracer` owns an atomic raw writer pointer protected by `InstrumentedMutex`; `StartTrace` stores options, resets get-id counter to 1, takes ownership of the writer, and writes the header; `EndTrace` deletes the writer; `WriteBlockAccess` double-checks writer presence around sampling and locking; `NextGetId` returns reserved ID 0 when tracing is off and skips 0 on wrap. Dependencies include RocksDB trace reader/writer APIs, `TraceType`, `TableReaderCaller`, `BlockCacheTraceRecord`, `SystemClock`, coding helpers, internal-key helpers, and hash utilities. Risks include raw pointer ownership, CSV parsing that cannot handle commas in CF names, unchecked trailing bytes after access decode, max-file-size checks allowing one record beyond the limit, and reliance on internal key/block key layouts. Test signals in `block_cache_tracer_test.cc` cover headers, start/stop behavior, get-id behavior, mixed block type field gating, and human-readable round-trip reconstruction.
