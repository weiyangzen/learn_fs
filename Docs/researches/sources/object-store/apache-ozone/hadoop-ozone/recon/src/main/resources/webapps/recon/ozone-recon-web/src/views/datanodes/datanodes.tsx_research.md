# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/datanodes/datanodes.tsx

Purpose: Legacy class-component Datanodes page. It lists datanodes, displays health/operational state, storage and pipeline details, overlays decommissioning status, and allows removing dead datanodes from Recon tracking.

Important APIs/types/functions: Defines datanode/pipeline interfaces, render helpers `renderDatanodeState`, `renderDatanodeOpState`, local `getTimeDiffFromTimestamp`, table `COLUMNS`, and class methods `_loadData`, `_loadDecommisionAPI`, `_loadDataNodeAPI`, `removeDatanode`, selection handlers, and confirmation handlers. Uses `AxiosGetHelper` for `/api/v1/datanodes/decommission/info` and `/api/v1/datanodes`, `AxiosPutHelper('/api/v1/datanodes/remove')`, `AutoReloadHelper`, `ColumnSearch`, `StorageBar`, `ReplicationIcon`, and `DecommissionSummary`.

Control flow: Each refresh first fetches decommission info to collect UUIDs, then fetches datanodes and maps rows into table data. If a UUID appears in the decommission set and is not already `DECOMMISSIONED`, displayed `opState` is forced to `DECOMMISSIONING`. Auto reload starts on mount. Row selection is enabled only for records with state `DEAD`; confirming removal sends selected row keys to the remove endpoint and reloads.

State and persistence: Local state stores loading, row data, total count, selected columns, selected row keys, and last update. Module-level globals hold cancellation controllers and `decommissionUuids`, which are shared across component instances. No persisted storage.

Dependencies and integration points: Integrates with Recon datanode and decommission endpoints, Ant Design Table/Popover/Popconfirm, storage/pipeline visualization components, and legacy auto reload.

Risks: Module-level `decommissionUuids` is read inside column renderers, making rendering depend on shared mutable state outside React. `lastHeartbeat` is typed as string in the backend response but treated numerically in table rows. Errors in the decommission call prevent the datanode call from showing otherwise valid data. `removeDatanode` reuses `cancelSignal` also used for datanode GET requests. `onDisable` returns `undefined` for enabled rows, relying on Ant Design truthiness.

Test signals: Tests should cover sequential decommission+datanode fetches, display override for decommissioning UUIDs, row selection disabled for non-DEAD nodes, remove PUT payload and reload, pipeline popovers, storage rendering, search/filter columns, and cancellation on unmount.
