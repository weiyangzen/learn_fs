## sources/storage-engines/rocksdb/table/block_based/block_builder.cc

Purpose: implements `BlockBuilder`, the writer for RocksDB block payloads. It emits prefix-compressed key/value entries, restart arrays, optional data-block hash indexes, optional separated key/value storage, timestamp-stripped keys, value-delta encoded index values, and a `DataBlockFooter` describing encoded features.

Important APIs/functions: constructor initializes restart state and optional `DataBlockHashIndexBuilder`; `Reset()` and `SwapAndReset()` clear builder state; `EstimateSizeAfterKV()` predicts size after adding one entry; `Finish()` appends values, restart offsets, optional hash index, and footer; `Add()` stores and maintains `last_key_`; `AddWithLastKey()` uses caller-provided previous key; `AddWithLastKeyImpl()` is the hot encoding path; `MaybeStripTimestampFromKey()` applies user-defined timestamp stripping; `GetRestartKey()` decodes restart-point keys; `ScanForUniformity()` marks blocks suitable for auto/interpolation search using restart-key gap coefficient of variation.

Control flow: each add strips timestamps as configured, maybe starts a new restart interval, computes shared prefix bytes unless delta encoding is disabled or skipped, emits varint headers, writes the non-shared key delta, and writes either the full value or caller-provided delta value. With separated KV storage, values go into `values_buffer_` and restart entries include a value offset. On finish, the values section is appended before restarts, then the footer is encoded.

State and persistence behavior: persistent on-disk state is the serialized block buffer, restart offsets, optional hash index payload, and footer bits. In-memory mutable state includes `buffer_`, `values_buffer_`, `restarts_`, `estimate_`, `counter_`, `last_key_`, `finished_`, `is_uniform_`, and hash-index builder state. The implementation assumes input slice sizes fit in 32 bits and notes unchecked 4 GiB buffer overflow risks for huge blocks.

Dependencies/integration points: uses `dbformat` for internal key/timestamp helpers, `block_util.h` decoders and `ReadBe64FromKey`, `DataBlockFooter`, `DataBlockHashIndexBuilder`, `BlockBasedTableOptions`, `Statistics`, and RocksDB coding helpers. Readers in `block.cc` and tests in `block_test.cc` must decode exactly this layout.

Risks: callers must not mix `Add()` and `AddWithLastKey()` between resets; delta values must match value-delta encoding semantics; timestamp stripping must also be done by callers for timestamp-bearing values such as first internal keys; separated-KV changes footer size and decode boundaries; format-bit changes require careful backward compatibility.

Test signals: `block_test.cc` exercises plain/data hash blocks, separated KV, user-defined timestamps, value-delta index blocks, uniformity detection, interpolation search, checksums, and corruption boundaries. `block_based_table_reader_test.cc` validates the produced blocks through real table reads.
