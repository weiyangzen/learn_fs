<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/range.go -->
# sources/storage-engines/foundationdb/bindings/go/src/fdb/range.go

Purpose: defines range abstractions and range-read iteration behavior.

Important APIs: `KeyValue`, `RangeOptions`, `Range`, `ExactRange`, `KeyRange`, `SelectorRange`, `RangeResult`, `RangeIterator`, `Strinc`, and `PrefixRange`.

Control flow: `RangeResult.Iterator` creates a `RangeIterator` around the first future. `Advance` waits for a pending batch; `Get` returns current item and triggers `fetchNextBatch` at batch boundaries. `fetchNextBatch` updates begin/end selectors based on direction, decrements remaining limit, increments iteration, and calls `doGetRange`. `GetSliceWithError` forces modes optimized for exact/want-all reads.

State and persistence: no writes. Iterator tracks transaction pointer, selectors, range options, batch future, index, errors, and snapshot flag.

Dependencies and integration: uses `Transaction.doGetRange`, key selector helpers, and C range streaming modes from generated code.

Risks: iterator is explicitly not safe for concurrent use or copying. `fetchNextBatch` assumes at least one kv when called. Prefix helpers reject empty/all-0xFF prefixes; callers must handle errors. Range reads returned from `Transact` can outlive transactions and are documented unsafe.

Test signals: `ExamplePrefixRange` and `ExampleRangeIterator` cover basic prefix and iteration behavior. Edge cases such as reverse/limit/multi-batch/errors need additional coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/fdb/range.go -->
