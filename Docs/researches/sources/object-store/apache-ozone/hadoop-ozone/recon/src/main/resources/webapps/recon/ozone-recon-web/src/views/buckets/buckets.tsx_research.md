# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/buckets/buckets.tsx

Purpose: Legacy class-component Buckets page. It lists buckets with volume filtering, column selection, limit selection including custom values, quota bars, ACL drawer, and auto reload.

Important APIs/types/functions: Defines backend response interfaces, `IBucketsState`, limit options, render helpers for versioning/storage type/bucket layout, mutable `COLUMNS`, and class methods `_addAclColumn`, `_handleColumnChange`, `_handleLimitChange`, `_onCreateOption`, `_handleVolumeChange`, `_getSelectedColumns`, `_handleAclLinkClick`, `_getVolumeSearchParam`, and `_loadData`. Uses `AxiosGetHelper('/api/v1/buckets', ..., {limit})`, `AutoReloadHelper`, `ColumnSearch`, `QuotaBar`, `AclPanel`, `MultiSelect`, and `CreatableSelect`.

Control flow: Constructor injects an ACL column into module-level column arrays and initializes auto reload. On mount, an optional `volume` query parameter preselects a volume, `_loadData` fetches buckets, maps backend `name` to UI `bucketName`, builds a `Map<volume, Set<bucket>>`, builds volume options, and selects all volumes or preserves prior selection. Rendering filters `COLUMNS` by selected columns and applies `ColumnSearch` to searchable columns. Unmount stops polling and aborts the latest request.

State and persistence: Local state stores loading, total count, selected columns/volumes/buckets, volume map/options, current ACL row, drawer visibility, selected limit, and refresh timestamp. No storage persistence. Module-level `COLUMNS`, `defaultColumns`, and `cancelSignal` are shared across instances.

Dependencies and integration points: Integrates with `/api/v1/buckets`, legacy OM types, common ACL drawer, quota bars, Ant Design Table, React Router location search, and the legacy auto-reload helper.

Risks: Mutating module-level `COLUMNS`/`defaultColumns` can leak across reloads or tests. `_onCreateOption` accepts `parseInt(created)` truthiness, rejecting `0` but accepting partially numeric strings in some cases. `selectedVolumes` can contain the all-volumes sentinel `*`; `_handleVolumeChange` ignores it unless the real volume options are also included. Request cancellation uses a module global controller. Query-param typing assumes `props.location.search` exists although props are declared generically.

Test signals: Tests should cover URL volume preselection, fetch mapping, all-volume selection, custom limit validation, ACL column/drawer behavior, quota columns, column search injection, polling start/stop, and aborted in-flight requests on unmount.
