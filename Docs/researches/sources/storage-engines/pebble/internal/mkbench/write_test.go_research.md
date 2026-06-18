<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/write_test.go -->
# sources/storage-engines/pebble/internal/mkbench/write_test.go

Purpose: integration-style fixture tests for the write-throughput parser.

Important APIs/functions: constants and variables for fixture paths, `TestParseWrite_FromScratch`, and `TestParseWrite_Existing`.

Control flow and state: from-scratch tests create a temp output directory, call `parseWrite`, and compare generated top-level and per-run summaries to fixtures. Existing-data tests copy raw fixture data, remove one day, generate partial summaries, assert the top-level summary differs and only remaining-day per-run files exist, then parse the full data into the same summary dir and assert it converges to fixtures.

Dependencies and integration: uses `copyDir`, `filesEqual`, `maybeSkip`, `dataDirPaths`, `os`, `filepath`, `strings`, and `testify/require`. It covers both real and symlinked input roots. Risks not covered include malformed raw lines beyond skip behavior, multiple workloads, corrupt existing JSON, and output directory creation failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/write_test.go -->
