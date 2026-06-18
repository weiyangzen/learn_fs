## sources/storage-engines/tikv/components/resource_metering/src/recorder/sub_recorder/summary.rs

Purpose: records explicit per-request summary counters such as read/write keys, network bytes, and logical IO bytes from thread-local resource metering context.

Important APIs/types/functions: public functions `record_read_keys`, `record_write_keys`, `record_network_in_bytes`, `record_network_out_bytes`, `record_logical_read_bytes`, and `record_logical_write_bytes`; `SummaryRecorder` implements `SubRecorder`. Network/logical byte functions are gated by `ENABLE_NETWORK_IO_COLLECTION`.

Control flow: public record functions update atomics in `STORAGE` for the current thread. On `collect`, the recorder drains each thread’s completed `summary_records`, merges them into `RawRecords`, separately snapshots the currently attached tag’s live `summary_cur_record`, and propagates the enabled switch to local storage.

State/persistence: all counters are in thread-local/in-memory local storage. `pause` clears per-thread `summary_enable`; `resume` sets it; `thread_created` initializes new thread state from the recorder’s current enabled flag.

Dependencies/integration: integrated with local storage, global network collection config, and raw record summary merge methods. The reporter later aggregates these summary fields by resource tag or region.

Risks: byte counters are silently dropped when network IO collection is disabled; current-record collection requires non-empty `extra_attachment`; lock contention is possible around per-thread summary maps; enable state only reaches threads during collect/thread creation.

Test signals: summary integration tests verify no data before a data sink activates collection, correct read/write key reporting while active, and no data after the sink unregisters.
