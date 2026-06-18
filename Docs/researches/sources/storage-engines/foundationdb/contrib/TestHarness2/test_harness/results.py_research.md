# sources/storage-engines/foundationdb/contrib/TestHarness2/test_harness/results.py

Purpose: CLI/reporting layer for Joshua ensemble summaries. It prints per-error reproduce details and aggregate code-probe/runtime statistics.

Important APIs/types: `GlobalStatistics`, `EnsembleResults`, `write_header`, and `write_footer`. `EnsembleResults.dump()` emits `EnsembleResults`, `CodeProbe`, and optionally per-test runtime nodes.

Control flow: main configures pretty output, prints an XML/JSON envelope, tries to import Joshua summary printer, then computes coverage status from FDB coverage counts and runtime stats. Exit code is nonzero when coverage is not OK.

State and persistence: read-only from FDB via `test_harness.fdb.Statistics` and `read_coverage`.

Dependencies and integration: config filters, `SummaryTree`, `Coverage`, `quoteattr`, optional Joshua package. Consumed by humans/automation inspecting ensembles.

Risks and test signals: `ratio` is calculated before `total_test_runs` is populated, so missed-probe threshold may be wrong; JSON header formatting is hand-built. Test coverage-disabled mode, empty coverage, missed non-rare probe errors, and missing Joshua import warning.
