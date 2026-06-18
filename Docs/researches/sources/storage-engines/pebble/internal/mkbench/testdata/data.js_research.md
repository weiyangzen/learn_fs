<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/testdata/data.js -->
# sources/storage-engines/pebble/internal/mkbench/testdata/data.js

Purpose: expected cooked YCSB benchmark fixture used by mkbench tests.

Important data shape: JavaScript assignment `data = { ... };` mapping workload names like `ycsb/A/values=1024` to newline-delimited CSV strings. Each CSV line encodes day, ops/sec, read bytes, write bytes, read amplification, and write amplification.

Control flow and state: no executable control flow. The file represents merged, sorted, cooked output for two days of fixture data and multiple YCSB workloads/value sizes. It also acts as an existing cooked input in incremental parsing tests.

Dependencies and integration: consumed by `ycsbLoader.loadCooked`, `parseYCSB`, and tests comparing generated output with `filesEqual`. Persistence behavior is fixture-based: parser output must be byte-equivalent after JSON pretty printing and semicolon wrapping. Risks include fixture drift if formatting changes, lack of schema validation beyond parser assumptions, and JavaScript wrapper format being required by older visualization code.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/testdata/data.js -->
