## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/TSSComparison.h

Purpose: Declares the comparison and metric hooks used when load balancing duplicates requests to a testing storage server or compares storage replicas.

Important APIs/types/functions: `DetailedTSSMismatch` stores mismatch ID, timestamp, and trace string. `TSSMetrics` contains counters for requests, stream comparisons, SS/TSS errors, TSS timeouts, mismatches, DDSketch latency distributions for several request kinds, error-code maps, detailed mismatch records, and methods `ssError()`, `tssError()`, `recordLatency()`, `shouldRecordDetailedMismatch()`, `recordDetailedMismatchData()`, and `clear()`. Template declarations `TSS_doCompare`, `LB_mismatchTraceName`, and `TSS_traceMismatch` are implemented for concrete storage request/reply types elsewhere.

Control flow: `LoadBalance.actor.h` increments counters and calls type-specific compare/trace hooks after both source and TSS/replica responses complete. Detailed mismatch recording is rate-limited to a small number per metrics interval.

State and persistence behavior: Metrics and detailed mismatches are in-memory and reference-counted. Detailed mismatch data can be later surfaced through database context or traces; this header itself does not persist it.

Dependencies and integration points: Depends on `Stats.h`, `DDSketch`, and unordered maps. It is the decoupling layer between generic fdbrpc load balancing and storage-specific comparison logic in storage server interface code.

Risks: Missing template specializations cause link/build failures for new request types used with TSS comparison. `shouldRecordDetailedMismatch()` increments the mismatch counter as a side effect. Detailed mismatch vectors can grow within intervals if callers do not clear as expected.

Test signals: Counter increments by error/timeout/mismatch path, latency sketch updates by request type, detailed mismatch throttling/clear, and concrete compare/trace specializations for every request type that enables TSS or replica comparison.
