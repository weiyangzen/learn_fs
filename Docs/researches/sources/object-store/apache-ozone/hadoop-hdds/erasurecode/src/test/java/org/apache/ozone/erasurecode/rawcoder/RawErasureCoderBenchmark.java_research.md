<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/RawErasureCoderBenchmark.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/RawErasureCoderBenchmark.java

## Purpose
`RawErasureCoderBenchmark` is a command-line benchmark for raw encoder/decoder throughput across dummy, RS Java/native, and XOR Java/native coders.

## Important APIs, Types, and Functions
It defines `TARGET_BUFFER_SIZE_MB`, `MAX_CHUNK_SIZE`, coder factory list, `main`, `performBench`, `getRawEncoder`, `getRawDecoder`, `getBufferForInit`, `printThreadStatistics`, `genTestData`, `BenchData`, and `BenchmarkCallable`.

## Control Flow
The benchmark parses operation, coder index, thread count, data length, chunk size, and direct-buffer mode; initializes per-thread data; runs callables through an executor; times loops; and prints throughput/statistics.

## State and Persistence Behavior
State is in-memory benchmark buffers and per-thread callable counters. No files are written.

## Dependencies and Integration Points
It depends on raw coder factories, `ECReplicationConfig(6,3)`, Guava preconditions, random data, executor services, and Hadoop `StopWatch`.

## Risks and Test Signals
Risks include benchmark-only assumptions about RS 6+3, memory pressure from target buffer sizing, native availability differences, and use of benchmark code as a test. Signals include the benchmark test smoke-running dummy/RS paths and manual throughput comparisons.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/RawErasureCoderBenchmark.java -->
