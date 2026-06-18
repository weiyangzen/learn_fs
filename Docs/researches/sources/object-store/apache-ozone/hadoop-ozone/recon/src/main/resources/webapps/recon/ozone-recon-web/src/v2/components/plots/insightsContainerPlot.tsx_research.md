# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/plots/insightsContainerPlot.tsx


Purpose: Pie chart for container size distribution in Insights.

Important APIs/types/functions: `ContainerSizeDistribution`, `ContainerSizeDistributionProps`, `ContainerPlotData`, `updatePlotData`, and ECharts pie options.

Control flow/state/persistence: Aggregates `containerCountResponse` by `containerSize` into a `Map`, derives human-readable power-of-two ranges, stores plot data in state, and updates on response changes. If `containerSizeError` exists, overlays a “No data available” graphic.

Dependencies/integration points: Used by V2 Insights pages and V2 EChart wrapper.

Risks/test signals: `rgba(256, 256, 256, 0.5)` uses out-of-range RGB values. Map key order follows response order, not sorted, so legend/range order can be inconsistent.
