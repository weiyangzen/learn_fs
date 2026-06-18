# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/deletePendingDirsTable.tsx

Purpose: Displays OM directories pending deletion with limit selection and debounced name search.

Important APIs, types, and functions: Exports `DeletePendingDirTable`. Props include shared pagination, selected limit, and limit-change handler.

Control flow: Uses `/api/v1/keys/deletePending/dirs?limit=...`, copies `deletedDirInfo` into local rows, refetches on limit changes, filters by directory key, and renders size/time/path columns.

State and persistence behavior: Local `data` and `searchTerm`; API state is from `useApiData` with no persistence.

Dependencies: Uses AntD table, shared `Search`, `SingleSelect`, `LIMIT_OPTIONS`, `useDebounce`, `useApiData`, `byteToSize`, and moment utils.

Integration points: Part of the Insights pending-deletion views.

Risks and edge cases: `initialFetch: false` means the refetch effect owns initial loading. Row key is only `key`, which may collide across paths. Search only checks `key`, not full path.

Test signals: Cover limit refetch, duplicate directory names under different paths, zero/large sizes, timestamp formatting, and disabled search when no rows exist.
