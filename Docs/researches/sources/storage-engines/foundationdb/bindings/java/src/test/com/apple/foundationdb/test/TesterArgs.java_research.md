# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/TesterArgs.java

Purpose: command-line parser and immutable-ish configuration holder for Java performance test runners.

Important APIs and flow: `parseArgs` recognizes output directory, subspace, disabling multiversion API, enabling callbacks on external threads, using external client, and a list of tests to run. It prints usage and throws on malformed or unknown arguments. Accessors expose parsed booleans, `Subspace`, output directory, and test names.

State and persistence: stores configuration in object fields; no database or filesystem writes. Dependencies include `Subspace` and `Tuple`. Integration is with `AbstractTester`, `PerformanceTester`, and `RYWBenchmark`. Risks include returning null on help, typo in one error message, no quoting support beyond shell argv, and parsing tests until the next dash-prefixed token. Signal is argument validation before benchmarks run.
