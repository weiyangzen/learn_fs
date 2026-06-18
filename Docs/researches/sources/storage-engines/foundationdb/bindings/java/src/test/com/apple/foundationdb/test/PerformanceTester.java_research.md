# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/PerformanceTester.java

Purpose: configurable Java binding performance suite for core Completable API operations, producing KPI JSON through `AbstractTester`/`TestResult`.

Important APIs and flow: constructor registers enum `Tests` to benchmark methods for future latency, set/clear/clear range, parallel and serial get, range reads, key selectors, single-key ranges, alternating get/set, and write transactions. `testPerformance` loads data, selects requested tests from `TesterArgs`, sleeps for quiescence, runs each test multiple times, and records the median keys/sec. `insertData` clears the configured subspace and fills deterministic fixed-width keys using concurrent `runAsync` actors.

State and persistence: actively clears and repopulates either user space or a configured subspace, then may perform canceled mutations or committed write transactions. Dependencies include `AbstractTester`, `TesterArgs`, `TestResult`, `AsyncUtil`, `ByteArrayUtil`, and transaction retry APIs. Risks include destructive clears without a subspace, benchmark sensitivity to cluster load, large sleeps, and tests that use canceled transactions as client-side mutation benchmarks. Signal is KPI output plus captured errors.
