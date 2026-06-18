<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/testdata/write-throughput/20211028-pebble-write-size=1024-run_1-summary.json -->
# sources/storage-engines/pebble/internal/mkbench/testdata/write-throughput/20211028-pebble-write-size=1024-run_1-summary.json

Purpose: expected per-run write-throughput summary fixture for the 20211028 `write/values=1024` benchmark.

Important data shape: JSON object keyed by raw input paths, each containing `opsSec` and `rawData` CSV. It mirrors the 20211027 fixture for a later day with different optimal split and write amplification results.

Control flow and state: static fixture only. It preserves full raw cooked datapoints so tests can verify both summary scoring and provenance-preserving output filenames.

Dependencies and integration: used by write parser tests through `testdataPerRunSummaryFilenames`. The top-level summary fixture points to this filename, and incremental tests verify it is produced when 20211028 data remains. Risks are the same as the 20211027 fixture: large raw string fragility, byte-for-byte formatting dependence, and limited semantic validation beyond fixture comparison.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/testdata/write-throughput/20211028-pebble-write-size=1024-run_1-summary.json -->
