## sources/storage-engines/rocksdb/table/block_based/block_builder.h

Purpose: declares `BlockBuilder`, the block-format writer used by table builders for data, index, range tombstone, and metadata-style blocks. It exposes a compact append/reset/finish API while hiding format details such as prefix compression, restart intervals, hash indexes, timestamp stripping, separated KV storage, and uniform-key detection.

Important APIs/types: constructor parameters control restart interval, key delta encoding, value delta encoding, data-block index type, hash-table utilization ratio, timestamp size and persistence, whether keys are user keys, separated KV storage, statistics, and uniform CV threshold. Public methods are `Reset()`, `SwapAndReset()`, `Add()`, `AddWithLastKey()`, `Finish()`, `CurrentSizeEstimate()`, `EstimateSizeAfterKV()`, `empty()`, `MutableBuffer()`, and `IsUniform()`.

Control flow: callers add strictly sorted keys until a block is ready, call `Finish()` to obtain a `Slice` into builder-owned memory, then `Reset()` or `SwapAndReset()` for reuse. `AddWithLastKey()` exists for call sites already tracking previous keys and avoids redundant state maintenance. The header documents invariants: no mixing `Add()` and `AddWithLastKey()`, no finish-before-reset appends, and keys larger than prior keys except for range tombstone blocks.

State and persistence behavior: fields in the class mirror serialized layout. `buffer_` stores encoded entries and final footer, `restarts_` stores restart offsets, `values_buffer_` temporarily stores separated values, `last_key_` supports prefix compression, `estimate_` tracks uncompressed size, `counter_` tracks restart interval position, and `is_uniform_` records the most recent finished block’s uniformity bit.

Dependencies/integration points: includes RocksDB `Slice`, public table options, and `DataBlockHashIndexBuilder`. It is consumed by block-based table builders and by tests constructing synthetic blocks.

Risks: constructor flags must match the block reader path. Mis-setting `is_user_key_`, timestamp persistence, or value-delta encoding can produce blocks that decode incorrectly. The `Slice` returned by `Finish()` is invalidated by `Reset()`.

Test signals: parameterized tests instantiate the builder across restart intervals, timestamp modes, separated KV, data block hash indexes, and index block value-delta settings.
