# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/insights/insights.tsx

Purpose: Functional v2 Insights page that renders two utilization charts: file-size frequency distribution and container-size distribution.

Important APIs/types/functions: Uses `useApiData<FileCountResponse[]>('/api/v1/utilization/fileCount')` and `useApiData<any[]>('/api/v1/utilization/containerCount')`, then passes responses to `FileSizeDistribution` and `ContainerSizeDistribution`. Its state is `InsightsState` for volume/bucket filter metadata plus a `PlotResponse` wrapper for both datasets.

Control flow: Both API hooks fetch on mount. An effect waits until both hooks are no longer loading, then derives a `Map<volume, Set<bucket>>`, converts volume keys into `Option[]`, records per-API errors, and updates `plotResponse` with either real data or default one-row placeholders. Rendering shows a loading `Result`, then two Ant Design cards with chart components or "No Data" results.

State and persistence: All state is local and volatile. Volume/bucket maps are recalculated from the latest file-count response. There is no polling, URL state, or persisted selection in this page; downstream chart components own filter interaction.

Dependencies and integration points: Integrates with Recon utilization endpoints, v2 chart components, the v2 multi-select option type, Ant Design grid/card/result, and shared fetch-error notifications.

Risks: The effect closes over `state` but does not include it in the dependency list, so concurrent state changes could be overwritten. `containerCountAPI` is typed as `any[]` instead of `ContainerCountResponse[]`, weakening compile-time checks. Default placeholder rows make `length > 0` true and can render charts with sentinel data if an endpoint returns undefined. Error values are passed as `string | undefined` in the type but hook errors may be richer objects.

Test signals: Tests should mock partial and complete API success, per-endpoint failures, empty arrays, duplicate volume/bucket pairs, and ensure chart props receive stable volume options, bucket maps, data, and error flags.
