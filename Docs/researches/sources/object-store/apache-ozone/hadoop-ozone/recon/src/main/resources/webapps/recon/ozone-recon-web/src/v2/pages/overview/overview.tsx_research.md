# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/overview/overview.tsx

Purpose: v2 Recon Overview dashboard. It aggregates cluster health, capacity, object counts, OM sync status, and open/delete-pending key summaries into cards and summary tables.

Important APIs/types/functions: Uses four `useApiData` hooks for `/api/v1/clusterState`, `/api/v1/task/status`, `/api/v1/keys/open/summary`, and `/api/v1/keys/deletePending/summary`, all with `initialFetch:false`. Uses `useAutoReload(loadOverviewPageData)`, `AutoReloadPanel`, `OverviewHealthCard`, `OverviewSimpleCard`, `OverviewSummaryCard`, `CapacityBreakdown`, `WrappedInfoIcon`, and imperative `syncOmData` via `AxiosGetHelper('/api/v1/triggerdbsync/om')`. Helper `getSummaryTableValue` formats byte or count values.

Control flow: `loadOverviewPageData` refetches all four hooks and sets `lastRefreshed`. Auto-reload and manual reload call that function. The task-status response is searched for `OmDeltaRequest` and `OmSnapshotRequest` timestamps for display in `AutoReloadPanel`. `syncOmData` triggers OM DB sync and stores the backend status string. Rendering lays out health cards, capacity breakdown, object count cards, two OM summary cards linking to `/Om` with tab state, and service identifiers.

State and persistence: Local state only stores `omStatus` and `lastRefreshed`. `cancelOMDBSyncSignal` persists the active sync request controller across renders and is cancelled on unmount. There is no local storage. Hook data is managed by the custom hooks.

Dependencies and integration points: Integrates with Recon cluster state, task status, OM key summary, and DB sync endpoints. Links drive navigation to Datanodes, Containers, Capacity, Volumes, Buckets, Pipelines, and OM DB Insights tabs. Uses `filesize` for sizes and `moment` for refresh timestamps.

Risks: Because all hooks use `initialFetch:false`, first render depends on `useAutoReload` invoking the loader; if that hook does not fire immediately, cards can remain at defaults. `storageReport` is destructured from default data, so defaults must always include it. Other-used-space arithmetic can go negative if backend reports inconsistent capacity fields. `syncOmData` catches `Error` but Axios errors can have richer shape. Links use capitalized paths that must match route definitions exactly.

Test signals: Tests should cover initial auto-load, manual reload, OM sync success/failure/cancel, missing task statuses, capacity item calculations, summary formatting for `null`, empty strings, counts, and byte values, and route state for summary-card links.
