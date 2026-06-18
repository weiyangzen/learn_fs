# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/insights/om/om.tsx

Purpose: Legacy OM DB Insights page. It provides tabbed tables for container mismatch, open keys, delete-pending keys, deleted-container keys, and delete-pending directories, with shared limit selection and expandable key details.

Important APIs/types/functions: Defines column sets for mismatch, open keys, pending keys, deleted keys, pending dirs, and expanded container keys. Uses `AxiosGetHelper` for `/api/v1/containers/mismatch`, `/api/v1/keys/open`, `/api/v1/keys/deletePending`, `/api/v1/containers/mismatch/deleted`, `/api/v1/keys/deletePending/dirs`, and `/api/v1/containers/{id}/keys`. Key methods include `addexistAtColumn`, `handleExistsAtChange`, `addfsoNonfsoKeyColumn`, `handlefsoNonfsoMenuChange`, `_loadData`, fetch methods for each tab, `expandedKey`, `changeTab`, row expansion methods, column-search builders, and limit handlers.

Control flow: Constructor mutates module-level column arrays to add dropdown filter columns and initializes active tab from route state. `_loadData` dispatches to the fetch method matching the current tab. Each fetch cancels other outstanding tab requests, sets loading, calls its endpoint with selected limit/filter flags, and stores tab-specific data. Tab changes reset data, filters, expanded rows, and limit, then fetch the new tab. Container rows fetch keys on expansion. Delete-pending key groups are flattened for summary rows and use a module-level `keysPendingExpanded` array for expansion detail.

State and persistence: Local state stores tab data arrays, expanded rows, current filters, active tab, FSO flags, and selected limit. Module-level cancellation controllers, mutable columns, and `keysPendingExpanded` are shared across instances. No persistent storage.

Dependencies and integration points: Integrates with multiple Recon OM/SCM consistency endpoints, legacy `ColumnSearch`, `CreatableSelect`, Ant Design Table/Tabs/Dropdown/Tooltip, and v2 `ReplicationInfo` for open-key replication rendering.

Risks: `fetchMismatchContainers` appears to set `mismatchContainers` to `[]` when `containerDiscrepancyInfo` exists because of `response?.data?.containerDiscrepancyInfo && []`, likely dropping real mismatch data. Column arrays are mutated at module scope. Custom limit validation uses `parseInt` truthiness. Many props are typed generically while reading `props.location.state`. Multiple cancellation controllers are manually coordinated. `keysPendingExpanded` is global and can become stale across instances/tests.

Test signals: Tests should cover each tab's endpoint and data mapping, route-state initial tab, exists-at and FSO/non-FSO filters, limit changes and custom limits, mismatch data mapping bug, delete-pending aggregation/expansion, container key expansion success/failure, cancellation when switching tabs, and searchable columns.
