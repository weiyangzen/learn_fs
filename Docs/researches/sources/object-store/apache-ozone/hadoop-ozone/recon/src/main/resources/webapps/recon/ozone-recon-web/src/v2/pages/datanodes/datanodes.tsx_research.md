# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/datanodes/datanodes.tsx

Purpose: Top-level Datanodes page that combines datanode inventory, decommission info, visible columns, search, auto-reload, and dead-node removal confirmation.

Important APIs, types, and functions: Exports default `Datanodes`. Local functions handle column changes, removal, combined data load, selection, and modal OK/cancel.

Control flow: Uses three `useApiData` hooks for decommission info, datanodes, and PUT remove. Combined effect maps API datanodes to table rows and rewrites op state to `DECOMMISSIONING` for decommissioning UUIDs. Removal calls PUT then reloads and clears selection.

State and persistence behavior: Tracks lastUpdated/dataSource/columns, selected columns, selected rows, search term/column, and modal open. A module-level `decommissionUuids` mirrors API data. Auto-reload persists via `useAutoReload`.

Dependencies: Uses AntD Button/Modal/icons, moment, shared Search/MultiSelect/DatanodesTable/AutoReloadPanel, `useApiData`, `useDebounce`, and datanode types.

Integration points: Talks to `/api/v1/datanodes`, `/api/v1/datanodes/decommission/info`, and `/api/v1/datanodes/remove`; renders `DatanodesTable` and remove modal.

Risks and edge cases: Global `decommissionUuids` can leak stale data. Combined effect spreads stale `state`. It manually starts polling on mount even though `useAutoReload` already starts based on session storage, risking duplicate initial refresh. Search column type includes revision but options omit it.

Test signals: Cover data/decommission merge, remove success/error, modal cancel clearing rows, auto-reload no-duplicate behavior, selectable dead nodes only, search fields, and decommission op-state rewrite.
