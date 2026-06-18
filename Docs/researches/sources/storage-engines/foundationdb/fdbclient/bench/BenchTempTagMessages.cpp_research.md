# sources/storage-engines/foundationdb/fdbclient/bench/BenchTempTagMessages.cpp

Purpose: benchmarks vector reserve strategies for temporary `TagsAndMessage` buffers similar to TLog `commitMessages()` handling.

Important APIs and control flow: `createTestMessage` allocates random payload bytes and random `Tag` arrays in an `Arena`. Three benchmarks compare no reserve, heuristic reserve based on total bytes (`totalBytes / 150`, clamped 10..5000), and exact reserve. Timing excludes synthetic source-message generation via `PauseTiming`.

State and persistence: all data is transient in arena allocations and `std::vector<TagsAndMessage>`. It models message movement, not durable log writes.

Dependencies and integration: includes `FDBTypes.h`, `IRandom.h`, `Arena.h`, and Google Benchmark. The workload is tied to TLog temp tag message optimization analysis.

Risks: the heuristic is benchmarked with generated average sizes and exactly three tags per message; production distributions may differ. Moving `TagsAndMessage` objects does not include downstream serialization or network effects.

Test signals: benchmarks run for 10, 100, 1000, and 5000 messages at representative average sizes, setting item and byte counts.
