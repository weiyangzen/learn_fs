# sources/storage-engines/rocksdb/trace_replay/trace_replay.h

## Purpose

Declares the shared tracing envelope and operation `Tracer` used to capture RocksDB query operations for later analysis or replay.

## Important APIs, Control Flow, And Dependencies

The header defines `kTraceMagic`, envelope size constants, trace file version 0.2, `Trace`, `TracePayloadType`, `TracerHelper`, and `Tracer`. `TracePayloadType` assigns stable bitmap positions for write batch data, get CF/key, iterator CF/key/bounds, and multiget size/CFIDs/keys. `Tracer` exposes methods for write, get, iterator seek, seek-for-prev, multiget overloads, max-size checks, write-order preservation, and closing with a footer.

## State, Persistence, Integration, Risks, And Test Signals

`Trace` is the serialized unit persisted by `TraceWriter`. `Tracer` owns a `TraceWriter`, `TraceOptions`, sampling count, and trace write status. It integrates with RocksDB operation hooks and downstream `TracerHelper::DecodeTraceRecord` consumers. Risks include keeping enum bitmap order backward compatible, filter/sampling interactions that can hide operations from analysis, and callers needing to close traces to emit `kTraceEnd`. Test signals come from trace-analyzer tests and any replay users that depend on the common format.
