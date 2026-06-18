# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/pipelines/pipelines.tsx

Purpose: v2 Pipelines page that lists SCM pipelines with column selection, pipeline-ID search, and auto-reload controls.

Important APIs/types/functions: Uses `useApiData<PipelinesResponse>('/api/v1/pipelines')`, `useAutoReload`, `useDebounce`, `PipelinesTable`, v2 `Search`, and `MultiSelect`. `defaultColumns` is derived from `PipelinesTable.COLUMNS`.

Control flow: The hook is configured with `initialFetch:false`; `loadPipelinesData` calls `refetch` and is wired to auto reload and manual reload. When data changes, an effect stores the pipelines as `activeDataSource` and updates `lastUpdated`. UI changes update selected columns and the search term; debounced search is passed to the table.

State and persistence: Local state holds active rows, available column options, and last update timestamp. Separate local state tracks selected columns and search term. No persistence or URL state is used.

Dependencies and integration points: Integrates with `/api/v1/pipelines`, shared reload panel, v2 table/search/select components, and pipeline type definitions.

Risks: The data effect spreads `state` from the closure and omits `state` from dependencies, so unrelated state fields can become stale if extended later. `defaultColumns` assumes every table column title is either a string or callable returning props with `children[0]`; table-column title changes can break label generation. With `initialFetch:false`, first load depends on auto-reload hook behavior.

Test signals: Tests should cover refetch on mount/auto reload/manual reload, column selection and tag close, search debounce passed to the table, disabled search when no rows exist, and behavior when the API returns empty or malformed pipeline arrays.
