# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/plots/heatmapPlot.tsx


Purpose: AG Charts treemap renderer for Heatmap data.

Important APIs/types/functions: `HeatmapPlot`, `capitalize`, `tooltipContent`, treemap `heatmapConfig`, and `AgChartsReact`.

Control flow/state/persistence: Builds chart options from `data`, `colorScheme`, and `entityType`. Tooltip shows size, access count or max access count, and entity name. Node click drills into `data.path` only for non-leaf/group nodes without `color`.

Dependencies/integration points: Used by V2 Heatmap page with `HeatmapResponse` and path update callback.

Risks/test signals: Tooltip content is HTML string with interpolated labels. `if (!data.color) if (data.path)` is terse and may misclassify nodes if color is falsy. No tests in this subset cover it.
