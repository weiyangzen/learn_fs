# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/plots/nuPieChart.tsx

Purpose: Renders the namespace-usage pie chart for a path, converting Recon namespace usage responses into ECharts pie slices with an optional synthetic `Other Objects` slice.

Important APIs, types, and functions: Exports `NUPieChart`. Props include `path`, `limit`, `size`, `subPaths`, `subPathCount`, `sizeWithReplica`, and `loading`. Local helpers are `getSubpathSize`, `updatePieData`, and `handleLegendChange`.

Control flow: The component derives visible subpaths, slices to the requested limit, computes percentages against total path size, inflates positive pie values by `MIN_BLOCK_SIZE` for visibility, and sends an `option` object to `EChart`. A legend-selection event recomputes the subtotal shown under the chart.

State and persistence behavior: Stores only `subpathSize` in React state. It recalculates on `subPaths` or `limit` changes and memoizes pie data from path/subpath/limit inputs. There is no persistent browser storage.

Dependencies: Depends on the local `EChart` wrapper, `byteToSize`, and the `NUSubpath` namespace-usage type.

Integration points: Used by the namespace-usage page to visualize children of the currently selected volume, bucket, directory, or key path.

Risks and edge cases: `getSubpathSize` takes an argument but tests `subPaths.length` from props, so stale closure behavior can affect filtered legend totals. `sizeWithReplica - remainingSize` looks suspicious for the synthetic replica size. Tooltip HTML is assembled manually and chart labels depend on path splitting.

Test signals: Cover empty paths, zero size, more subpaths than limit, exactly max-limit responses, key versus directory labels, legend-selection subtotal updates, and `sizeWithReplica === -1` handling.
