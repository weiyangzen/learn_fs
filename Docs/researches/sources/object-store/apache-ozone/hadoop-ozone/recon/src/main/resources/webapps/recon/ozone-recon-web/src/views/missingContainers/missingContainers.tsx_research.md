# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/missingContainers/missingContainers.tsx

Purpose: Legacy Containers page focused on unhealthy containers. It displays Missing, Under-Replicated, Over-Replicated, and Mis-Replicated tabs with cursor-style pagination and expandable container keys.

Important APIs/types/functions: Defines unhealthy container/key response interfaces, key and container column sets, `IMissingContainersState`, and class methods `fetchUnhealthyContainers`, `onRowExpandClick`, `expandedRowRender`, `onShowSizeChange`, `searchColumn`, `fetchPreviousRecords`, `fetchNextRecords`, `itemRender`, and `changeTab`. Uses `/api/v1/containers/unhealthy/{state}?limit=...&minContainerId=...` or `maxContainerId=...`, `/api/v1/containers/{containerID}/keys`, `ColumnSearch`, and `cancelRequests`.

Control flow: Mount selects tab `1`, which maps to `MISSING` and fetches the first page. Tab changes reset data/counts/cursors/expanded rows and fetch the new state. Pagination next/prev uses cursor keys from the previous response. Page size changes reset `lastSeenKey` to `firstSeenKey - 1` then fetch next records. Expanding a row stores a loading row state, fetches keys, and renders an inner Ant Design table.

State and persistence: Local state stores loading, current container rows, count totals for all unhealthy states, expanded row data, current unhealthy state, page size, and first/last cursor keys. Two module-level abort controllers track container and row-expansion requests. No persistence.

Dependencies and integration points: Integrates with Recon unhealthy container and container key endpoints, Ant Design Table/Tabs/Tooltip, React Router `Link` for pagination controls, `filesize` for key sizes, and shared time formatting.

Risks: `IContainerResponse.unhealthySince` is typed as string but rendered/sorted as number. Cursor pagination does not track disabled prev/next states, so users can request invalid ranges. Aborting row expansion on collapse cancels the single global expansion controller, which can affect another expanded row. Count totals are reset on tab switch and repopulated from each endpoint response; if the endpoint omits cross-counts, labels can disappear.

Test signals: Tests should cover all tab state mappings, first/next/previous cursor URLs, page-size changes, row expansion success/error/collapse cancellation, count label rendering, searchable container ID column, and empty response cursor preservation.
