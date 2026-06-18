# sources/storage-engines/rocksdb/trace_replay/trace_replay.cc

## Purpose

Implements the common RocksDB operation trace envelope, header parsing, trace encoding/decoding, conversion from raw traces to `TraceRecord` subclasses, and the `Tracer` that records DB operations.

## Important APIs, Control Flow, And Dependencies

`TracerHelper::EncodeTrace` writes timestamp, one-byte type, payload length, and payload; `DecodeTrace` decodes the envelope but does not currently validate the payload length against the remaining slice. `ParseTraceHeader` parses tab-separated header fields for trace and RocksDB version. `DecodeTraceRecord` supports legacy version 0.1 payloads and version 0.2 payload maps for write, get, iterator seek/seek-for-prev, and multiget records. The `Tracer` constructor writes a header; `Write`, `Get`, `IteratorSeek`, `IteratorSeekForPrev`, and `MultiGet` build typed payloads with `TracePayloadType` bitmaps and call `WriteTrace`; `Close` writes a footer.

## State, Persistence, Integration, Risks, And Test Signals

The `Tracer` stores trace options, writer ownership, a sampling counter, and the first trace write error. `ShouldSkipTrace` enforces max file size, operation filters, and sampling frequency. Persistent state is the trace file emitted through the supplied `TraceWriter`. Integration points are RocksDB DB tracing APIs, `TraceRecord` decode classes, analyzer tooling, execution replay, block cache tracing, and IO tracing via the shared `Trace` envelope. Risks include payload-length decode not checking length, assert-heavy malformed-payload paths, `log2`-based bit iteration, version parsing that collapses major/minor digits into one integer, and trace write error state that must be propagated through later writes and `EndTrace`. Tests in the analyzer suite explicitly cover previous trace write error propagation, while trace analyzer/replay paths exercise decode behavior.
