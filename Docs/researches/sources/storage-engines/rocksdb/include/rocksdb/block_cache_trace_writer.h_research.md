# sources/storage-engines/rocksdb/include/rocksdb/block_cache_trace_writer.h

## Purpose
`block_cache_trace_writer.h` defines the public tracing records, options, abstract writer interface, and factory for capturing RocksDB block cache accesses. Table readers build `BlockCacheTraceRecord` values for cache lookups and inserts, then pass them to a `BlockCacheTraceWriter` implementation that serializes a trace header and per-access payloads through the generic trace infrastructure.

## Important APIs, Types, And Functions
`BlockCacheTraceRecord` is the central data structure. It records `access_timestamp`, `block_key`, `block_type`, `block_size`, `cf_id`, `cf_name`, `level`, `sst_fd_number`, `caller`, `is_cache_hit`, `no_insert`, `get_id`, `get_from_user_specified_snapshot`, `referenced_key`, `referenced_data_size`, `num_keys_in_block`, and `referenced_key_exist_in_block`. `kReservedGetId` is declared as a static reserved ID. The struct provides a default constructor and a full constructor for populating all fields.

`BlockCacheTraceOptions` controls sampling with `sampling_frequency`, defaulting to one captured request per request. `BlockCacheTraceWriterOptions` configures the built-in writer's `max_trace_file_size`, defaulting to 64 GiB.

`BlockCacheTraceWriter` is an abstract class with virtual destructor, `WriteBlockAccess(const BlockCacheTraceRecord&, const Slice& block_key, const Slice& cf_name, const Slice& referenced_key)`, and `WriteHeader()`. The method takes `Slice` references for string payloads to avoid extra copies.

`NewBlockCacheTraceWriter(SystemClock* clock, const BlockCacheTraceWriterOptions& trace_options, std::unique_ptr<TraceWriter>&& trace_writer)` allocates the built-in implementation that writes block cache trace events to a caller-provided `TraceWriter`.

## Control Flow
Tracing begins when a writer implementation writes a header through `WriteHeader()`, typically when tracing is initiated. During table-reader operations, each block cache lookup or insert produces a `BlockCacheTraceRecord`. The caller passes the record plus slice views of the block key, column-family name, and referenced key to `WriteBlockAccess()`.

Records distinguish lookup/insert context through `no_insert`, cache hit/miss through `is_cache_hit`, and higher-level operation through `TableReaderCaller`. Get and MultiGet details use `get_id`, snapshot flag, referenced key, useful referenced data size, number of keys found in a block, and false-positive indication. Sampling is controlled outside the record by trace options.

The built-in factory wires the block-cache trace writer to the generic trace writer. The comment describes each access as serialized with a timestamp and type followed by payload, and `max_trace_file_size` bounds output size for that implementation.

## State And Persistence Behavior
The header defines trace data, not RocksDB data persistence. Trace output is external diagnostic state written through `TraceWriter`. `BlockCacheTraceRecord` stores strings by value, while `WriteBlockAccess()` also accepts `Slice` views to avoid copying at serialization time; implementations must not retain those slice references beyond the call unless they copy the data.

`access_timestamp` is supplied in the record, and the built-in writer also receives a `SystemClock*`, implying timestamping and header metadata are clock-integrated in the implementation. Trace files may stop or roll/fail according to `max_trace_file_size` behavior implemented elsewhere.

## Dependencies And Integration Points
The header includes `rocksdb/options.h`, `rocksdb/system_clock.h`, `rocksdb/table_reader_caller.h`, `rocksdb/trace_reader_writer.h`, and `rocksdb/trace_record.h`. It depends on `Status`, `Slice`, `SystemClock`, `TraceWriter`, `TraceType`, and `TableReaderCaller`.

Integration points are block-based table readers, block cache lookup/insert code, Get/MultiGet instrumentation, generic trace reader/writer infrastructure, and any tooling that replays or analyzes block cache traces. Column-family and SST metadata fields connect cache events back to LSM placement.

## Risks
Tracing can be high-volume and performance-sensitive. Capturing every access with large keys/names can increase CPU, allocation, and I/O overhead; `sampling_frequency` and `max_trace_file_size` need enforcement by the implementation and trace owner. Missing or inconsistent fields can reduce trace replay fidelity, especially for Get/MultiGet false positives and useful data-size accounting.

The API passes string data both in the record and as slices. Implementations must avoid lifetime bugs by serializing immediately or copying slices. They also need to preserve status errors from the underlying `TraceWriter` so tracing failures do not masquerade as successful capture.

Schema compatibility matters for trace tools. Adding or reinterpreting `TraceType`, `TableReaderCaller`, or record fields can break readers unless versioned through the trace header. `kReservedGetId` must remain distinct from real Get/MultiGet IDs.

## Test Signals
Tests should cover header writing, serialization/deserialization compatibility, default and populated `BlockCacheTraceRecord` fields, lookup versus insert records, hit versus miss records, Get/MultiGet metadata, snapshot flag handling, false-positive blocks, size cap behavior, sampling frequency behavior, propagation of `TraceWriter` errors, and lifetime safety when the passed slices reference temporary buffers.
