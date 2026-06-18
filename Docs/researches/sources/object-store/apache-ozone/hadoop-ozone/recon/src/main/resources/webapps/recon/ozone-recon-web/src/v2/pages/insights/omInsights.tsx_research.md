# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/insights/omInsights.tsx

Purpose: v2 OM DB Insights page shell. It assembles tabbed OM/SCM consistency and key-state tables, shares a limit selector across them, and supports expandable rows for container-to-key details.

Important APIs/types/functions: Uses `ContainerMismatchTable`, `DeletedContainerKeysTable`, `DeletePendingDirTable`, `DeletePendingKeysTable`, `ExpandedKeyTable`, and `OpenKeysTable`. It relies on `AxiosGetHelper` for row expansion against `/api/v1/containers/{containerId}/keys`, `MismatchKeysResponse`, `ExpandedRow`, and a `react-select` `Option` limit value. Primary callbacks are `onRowExpandClick`, `expandedRowRender`, and `handleLimitChange`.

Control flow: The page reads `activeTab` from React Router location state, defaults to tab `1`, and renders five Ant Design tab panes. Expanding a container row sets a shared loading flag, fetches keys for the selected container, stores them in `expandedRowData[containerId]`, and renders an `ExpandedKeyTable` with a generated `uid`. Each tab table receives the selected limit, common pagination config, and limit-change handler.

State and persistence: Local state holds global `loading`, all expanded row data, and the selected limit. No state is persisted. `rowExpandSignal` keeps the most recent row-expansion `AbortController`, but there is no unmount cleanup in this component.

Dependencies and integration points: Integrates with multiple v2 insights table components that own their own endpoint fetches. Router state from Overview summary cards selects Open Keys or Delete Pending Keys. It uses Ant Design tabs/tooltips and the shared fetch helper.

Risks: `setLoading(false)` is not called in the row-expansion catch path, so failures can leave expanded tables loading. A single global loading flag can make one expanded row affect all expanded row tables. The expansion request is not cancelled on unmount. `expandedRowData` updates read from the closure, so rapid row expansions can drop prior rows. The `activeTab` location destructuring assumes `location.state` is an object when present.

Test signals: Tests should cover route-state tab selection, limit propagation to each table, successful and failed expansion fetches, multiple expanded containers, and unmount/cancel behavior if it is later added.
