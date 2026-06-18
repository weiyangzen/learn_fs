<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/testdata/write-throughput/summary.json -->
# sources/storage-engines/pebble/internal/mkbench/testdata/write-throughput/summary.json

Purpose: expected top-level cooked write-throughput summary fixture.

Important data shape: JSON maps workload name `write/values=1024` to sorted day summaries. Each summary includes `name`, `date`, averaged `opsSec`, averaged rounded `writeAmp`, and `summaryPath` pointing to a per-run summary JSON.

Control flow and state: no executable logic. The file is the aggregate output of `writeLoader.cookSummary`, mixing per-day cooked runs into a visualization-friendly time series.

Dependencies and integration: compared against generated `summary.json` by write parser tests. It must remain consistent with per-run fixture filenames and `writeRun.summaryFilename`. Risks include date sorting/merge logic changes requiring expected output updates, no coverage for multiple workloads beyond this single fixture, and byte-for-byte JSON indentation sensitivity.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/testdata/write-throughput/summary.json -->
