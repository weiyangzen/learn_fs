# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/volumes/volumes.tsx

## Purpose
This React class component renders the Recon Volumes page. It lists OM volume metadata, supports column selection, adjustable fetch limits, links from volumes to filtered bucket listings, and opens an ACL drawer for a selected volume.

## Important APIs, types, and functions
`IVolumeResponse` models backend volume rows from `/api/v1/volumes`; `IVolumesState` stores table rows, selected columns, column options, selected limit, ACL drawer state, and refresh metadata. `COLUMNS` defines sortable/searchable table columns for volume, owner, admin, creation/modification times, quota, namespace capacity, bucket link, and a dynamically injected ACL column. `_addAclColumn` mutates module-level `COLUMNS` and `defaultColumns`. `_loadData` fetches volumes using `AxiosGetHelper('/api/v1/volumes', ..., { limit })`.

## Control flow, state, and persistence
All state is in memory. The constructor injects the ACL column and initializes selected limit to 1000. `_loadData` ensures selected columns are populated, closes any ACL panel, fetches data, maps `IVolumeResponse` into `IVolume`, then updates table state and `lastUpdated`. Column selection uses `MultiSelect`; limit selection uses `CreatableSelect`, including user-created numeric limits. Unmount aborts the current request and stops polling.

## Dependencies and integration points
The component depends on Ant Design table, React Router `Link`, `react-select/creatable`, local `MultiSelect`, `AclPanel`, `QuotaBar`, `ColumnSearch`, `AutoReloadPanel`, and Recon axios/common utilities. Bucket drilldown is encoded as `/Buckets?volume=<name>`. The ACL drawer expects `IAcl[]` in each volume response.

## Risks and edge cases
`COLUMNS` and `defaultColumns` are module-level arrays mutated by each constructor; `_addAclColumn` tries to avoid duplicate ACL columns, but shared mutable table definitions can surprise tests and hot reload. `_onCreateOption` accepts `parseInt(created)` truthiness, so `0` is rejected but strings like `10abc` pass `parseInt`; `isValidNewOption` has the same partial-parse behavior. `currentRow` is initialized as `{}` despite `IVolume` expectations, so `currentRow.acls` and `currentRow.volume` can be undefined until a row is selected. Request cancellation uses direct abort rather than the shared `cancelRequests` helper.

## Test signals
No direct frontend tests are in this subset. Good coverage would verify ACL column injection idempotence, custom limit validation, API limit query params, bucket link query encoding, selected-column filtering, and drawer state reset on reload.
