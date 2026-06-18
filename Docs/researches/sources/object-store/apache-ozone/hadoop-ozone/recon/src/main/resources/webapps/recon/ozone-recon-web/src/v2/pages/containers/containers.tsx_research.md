# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/containers/containers.tsx

Purpose: Top-level Containers page for unhealthy container tabs, quasi-closed containers, export job submission/polling/download/delete, highlights, search, columns, and manual pagination.

Important APIs, types, and functions: Exports default `Containers` plus `PAGE_SIZE_OPTIONS`. Important helpers include `toContainer`, `fetchExportJobs`, `handleSubmitExport`, `downloadFile`, `deleteJob`, `fetchQuasiClosedCount`, `fetchTabData`, and pagination handlers.

Control flow: Loads cluster state and first missing-container page on mount, lazily loads tab data by unhealthy state, fetches one extra record to compute `hasNextPage`, maps quasi-closed responses into shared container rows, manages page history for previous navigation, polls export jobs while active, and renders `ContainerTable` for data tabs plus export job tables.

State and persistence behavior: Tracks highlight counts, page size, per-tab pagination/data/loading state, expanded rows, selected columns, search term/column, selected tab, export jobs/state/submitting, and a polling interval ref. Auto-reload state persists through `useAutoReload`.

Dependencies: Uses AntD Card/Tabs/Table/Select/Button/Progress/Tag/Tooltip/message, shared Search/MultiSelect/ContainerTable/AutoReloadPanel, `useApiData`, `fetchData`, `useAutoReload`, overview constants, and container/overview types.

Integration points: Consumes `/api/v1/clusterState`, `/api/v1/containers/unhealthy/:state`, `/api/v1/containers/quasiClosed`, and `/api/v1/containers/unhealthy/export` endpoints.

Risks and edge cases: There is a duplicated `key: 'submittedAt'` property in `submittedColumn`. Export duplicate checks block new exports even for completed jobs until delete. Polling uses raw fetch/fetchData and ignores polling errors. Shared search/columns apply across tabs, and expanded-row cache can outlive tab data.

Test signals: Cover each tab fetch URL/count update, cursor pagination and page-size reset, quasi-closed mapping/title, auto-reload reset, export submit 429/error/success, polling lifecycle, download/delete actions, duplicate export guard, and row expansion.
