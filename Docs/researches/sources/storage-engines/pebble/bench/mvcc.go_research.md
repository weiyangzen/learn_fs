# sources/storage-engines/pebble/bench/mvcc.go

## Purpose
`mvcc.go` contains CockroachDB-style MVCC scan helpers and a faux MVCC merger used by benchmarks that approximate CockroachDB storage workloads.

## Important APIs, Types, And Functions
Functions `mvccForwardScan` and `mvccReverseScan` scan a `DB` between encoded MVCC bounds. Exported `FauxMVCCMerger` names `cockroach_merge_operator` and delegates to Pebble's default merger.

## Control Flow
Each scan opens an iterator with lower/upper MVCC bounds, iterates forward or reverse, splits keys using `cockroachkvs.Split`, compares the timestamp suffix to the supplied timestamp, copies qualifying logical key/value bytes into `bytealloc.A`, and accumulates count and byte totals.

## State And Persistence Behavior
The helpers are read-only. They allocate transient byte buffers to force materialization of scanned data. The merger affects write/compaction semantics only when configured by benchmark options.

## Dependencies And Integration Points
Dependencies include `pebble`, `cockroachkvs`, and `bytealloc`. `scan.go` uses the scan helpers, and benchmark options in `db.go` and replay merger hooks share the Cockroach merger name.

## Risks And Edge Cases
The helpers count every internal MVCC version visited, not only versions copied after timestamp filtering. Iterator errors are not returned by these helpers, so callers only get count/bytes. The faux merger is not a full Cockroach merge implementation and should be interpreted as benchmark approximation only.

## Test Signals
No direct tests. Indirect validation occurs through scan benchmark sanity checks that expected row counts match.
