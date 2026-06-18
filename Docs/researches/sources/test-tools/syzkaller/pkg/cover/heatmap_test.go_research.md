# sources/test-tools/syzkaller/pkg/cover/heatmap_test.go

Purpose: verifies heatmap data construction and formatting transformations.

Important APIs/types/functions: `TestFilesCoverageToTemplateData`, `TestFormatResult`, and helper `makeTimePeriod`.

Control flow: data-construction tests cover empty input, a single file, and a directory tree across two periods, comparing exported fields of `templateHeatmap`. Formatting tests apply `DropCoveredLines0`, `FilterMinCoveredLinesDrop`, and `OrderByCoveredLinesDrop` to small hand-built trees and compare expected pruning, ordering, and negative summaries.

State and persistence: all inputs are in-memory `coveragedb.FileCoverageWithDetails` or template row fixtures.

Dependencies and integration: uses `civil.Date`, `coveragedb.MakeTimePeriod`, and testify assertions. It does not render templates or query Spanner.

Risks: comparisons skip unexported builder and aggregation maps via `assert.EqualExportedValues` for construction tests, so some internal state issues may be invisible. No URL escaping or subsystem heatmap behavior is tested.

Test signals: good coverage for the public heatmap tree semantics that web rendering depends on.
