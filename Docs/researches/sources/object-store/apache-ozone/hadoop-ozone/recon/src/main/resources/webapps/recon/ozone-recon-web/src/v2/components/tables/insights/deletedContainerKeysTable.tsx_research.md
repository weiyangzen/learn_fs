# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/deletedContainerKeysTable.tsx

Purpose: Shows containers with deleted keys for mismatch/deleted-container insights and delegates expanded key details to the parent.

Important APIs, types, and functions: Exports `DeletedContainerKeysTable`. Props include limit, pagination, limit-change handler, `onRowExpand`, and `expandedRowRender`.

Control flow: Fetches `/api/v1/containers/mismatch/deleted?limit=...`, stores `containers`, debounces ID search, and renders an expandable AntD table with pipelines listed inline.

State and persistence behavior: Local `data` and `searchTerm`; API state comes from `useApiData`.

Dependencies: Uses AntD table, `Search`, `SingleSelect`, `LIMIT_OPTIONS`, `useDebounce`, `useApiData`, and insights container types.

Integration points: Part of Insights deleted-container key drill-down flow.

Risks and edge cases: Row key is `containerId`, which is good, but pipeline rendering assumes nested `pipeline.id.id`. Search only filters ID and not pipeline. Initial fetch depends on the limit effect.

Test signals: Cover limit refetch, empty pipelines, malformed pipeline IDs, expansion callback, debounced search, and API error handling.
