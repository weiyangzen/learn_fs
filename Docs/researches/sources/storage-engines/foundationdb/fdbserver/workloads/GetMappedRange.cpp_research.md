# sources/storage-engines/foundationdb/fdbserver/workloads/GetMappedRange.cpp

## Purpose
Tester workload for the client `getMappedRange` API. It builds a synthetic primary-record plus secondary-index layout and validates that mapped range reads return index entries together with the corresponding record lookups or record subranges, including byte-limit, continuation, conflict, and read-your-writes behavior.

## Important APIs, types, and functions
`GetMappedRangeWorkload` derives from `ApiWorkload` and chooses either native or read-your-writes transaction wrappers. Helpers generate tuple-encoded `recordKey`, split `recordKey(i, split)`, `indexEntryKey`, values, and mapper tuples. Core actors are `fillInRecords`, `scanMappedRangeWithLimits`, `scanMappedRange`, `testSerializableConflicts`, `testRYW`, `reportMetric`, and `_start`. Validation inspects `MappedRangeResult`, `MappedKeyValueRef`, `GetValueReqAndResultRef`, and `GetRangeReqAndResultRef`.

## Control flow
Only client 0 runs. Setup chooses transaction type, then `_start` inserts 500 records plus index entries. Native transactions use snapshot reads; read-your-writes transactions sometimes branch into explicit serializable-conflict or RYW-error checks. The happy path scans index entries from record 10 through 489 with randomized byte limits, checks every mapped record, advances with `firstGreaterThan(result.back().key)` while `more` is set, and runs a small-request stress loop while status metrics are checked.

## State and persistence behavior
The workload persists tuple keys under the user prefix `("prefix","RECORD",...)` and `("prefix","INDEX",...)`. It also mutates the server knob `STRICTLY_ENFORCE_BYTE_LIMIT` for the scan and restores it afterward. Conflict tests deliberately write either index keys or mapped record keys before commit. No cleanup is done, so test data remains in the simulated database.

## Dependencies and integration points
Depends on tuple encoding, `ApiWorkload` transaction factories, FoundationDB transaction wrapper APIs, commit proxy mapped-range implementation, `StatusClient::statusFetcher`, client/server knobs, and Flow coroutine utilities. It disables Attrition because queue and conflict expectations are sensitive to heavy failure injection.

## Risks and test signals
Risks include global `recordSize`/`indexSize` assumptions from record 0, continued reliance on split-record shape, transient mapped subrange `more` requiring retry, and expected fallback errors depending on quick-get knobs. Test signals are ASSERTs on result ordering and values, result size versus row and byte limits, expected `not_committed`/`get_mapped_range_reads_your_writes`/mapper errors, and storage `query_queue_max` remaining below `queueMaxLength`.
