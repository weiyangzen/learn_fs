# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/MappedRangeQueryIntegrationTest.java

## Purpose
This integration/performance test compares ordinary index range queries plus per-record range reads with FoundationDB mapped range queries, while validating that mapped results reconstruct the expected record ranges.

## Important APIs, Types, and Functions
The class defines tuple-key helpers for index and record entries, `insertRecordWithIndex`, `insertRecordsWithIndexes`, `RangeQueryWithIndex`, `rangeQueryAndThenRangeQueries`, `mappedRangeQuery`, `validateRangeResult`, and `assertByteArrayEquals`. It uses `Transaction.getRange`, `Transaction.getMappedRange`, `MappedKeyValue`, `AsyncUtil.whenAll`, `Range.startsWith`, and `StreamingMode.WANT_ALL`.

## Control Flow
The test generates a UUID-backed prefix, inserts 1000 indexed records in batches of 100, then runs the ordinary query and mapped query once each over a random contiguous range of 100 logical records. The ordinary path scans index entries, launches record-range reads in parallel, waits for all, and validates each returned split. The mapped path passes a tuple mapper and validates returned index key/value, mapped range begin/end, and embedded range result for each record.

## State and Persistence Behavior
The test writes namespaced but persistent data under a random `mapped-range-query-<uuid>` prefix. It does not clear data afterward. Static `MAPPER` captures the static `PREFIX` and record mapper tuple.

## Dependencies and Integration Points
It heavily exercises mapped-range JNI marshalling, `MappedKeyValue.fromBytes`, range iterator behavior, tuple encoding, and server support for mapped range. The `main` path reads `FDB_CLUSTERS` via `MultiClientHelper`, while the JUnit test uses the default cluster and `RequiresDatabase`.

## Risks and Edge Cases
The performance instrumentation computes `qps` as `numQueries * 1000L / time`; if a query finishes within 0 ms, this can divide by zero. The test leaves data behind and uses only one query by default, so it is more of a smoke/performance comparison than exhaustive validation. `assertByteArrayEquals` compares printable strings rather than byte arrays, which gives readable failures but can obscure array identity concerns.

## Test Signals
Passing validates mapped range result count, index key/value preservation, mapper-derived range boundaries, and embedded range result content across JNI and Java object reconstruction.
