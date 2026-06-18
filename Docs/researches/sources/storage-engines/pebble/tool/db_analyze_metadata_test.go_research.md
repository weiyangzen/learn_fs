## sources/storage-engines/pebble/tool/db_analyze_metadata_test.go

Purpose: tests `printMetadataStats`, the final renderer for `db analyze-metadata`, with controlled synthetic distributions.

Important APIs/types/functions: `TestPrintMetadataStats` uses `datadriven.RunTest` over `testdata/analyze_metadata`. For the `print-metadata-stats` command, it manually populates a `metadataStats` value with representative per-level states, computes sampled and total file counts, calls `printMetadataStats`, and returns the table output for golden comparison.

Control flow: level fixtures cover L0 with partial sampling and two-level index files, L1 empty, L2 with files but no samples, L3 sampled files without two-level indexes, L4 very small files, L5 large files, and L6 sampled zero-valued data. Each level receives repeated `stat.Add` calls to exercise means, stddev percentages, p90/max percentiles, total extrapolation, and blank/zero branches.

State and persistence: no filesystem or DB state is used beyond the datadriven file. The test is deterministic because all values are synthetic.

Dependencies and integration: depends on `datadriven`, `manifest.NumLevels`, and the `stat`/`metadataStats` types from production code. It isolates formatting from table-reading behavior.

Risks: this test does not validate manifest replay, object provider opening, table property extraction, or sampling loop stop conditions. Because it tests exact rendered output, formatting changes require fixture updates even when semantics are unchanged.

Test signals: protects human-readable formatting, blank handling for empty/unsampled levels, zero mean rendering, percent sampled text, total extrapolations, and percentile rows.
