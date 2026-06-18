# sources/test-tools/syzkaller/pkg/cover/heatmap.go

Purpose: transforms database file coverage records into hierarchical heatmap template data and renders style/body/JS fragments.

Important APIs/types/functions: `templateHeatmapRow`, `templateHeatmap`, row methods `Filter`, `Transform`, `Sort`, `addParts`, `prepareDataFor`, `Visit`; `FilesCoverageToTemplateData`, `DoHeatMapStyleBodyJS`, `DoSubsystemsHeatMapStyleBodyJS`, `FormatResult`, `Percent` usage, and template helpers.

Control flow: records are inserted into a tree by optional subsystem plus file path parts. Each node aggregates instrumented/covered counts per `TimePeriod`. Columns are sorted by period end date and converted to percentages, covered counts, tooltips, summary values, and file coverage links. Formatting can filter small drops, remove zero-covered files, remove empty directories, and order by coverage drop while rewriting summaries to negative drop counts.

State and persistence: in-memory tree maps/slices. Rendering reads embedded `templates/heatmap.html`; database reads happen via `coveragedb.FilesCoverageWithDetails`.

Dependencies and integration: depends on `coveragedb`, `spannerclient`, embedded templates, and subsystem list side-effect import. It feeds web UI heatmap endpoints.

Risks: `DoSubsystemsHeatMapStyleBodyJS` panics on DB errors while `DoHeatMapStyleBodyJS` returns errors. `FormatResult` calls `slices.Max` on row coverage slices, so callers must avoid rows without coverage data or filter carefully. File coverage links concatenate query parameters without URL escaping.

Test signals: `heatmap_test.go` validates tree construction, date columns, links, and formatting filters/order.
