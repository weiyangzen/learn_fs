# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/volumes/volumes.tsx

Purpose: v2 Volumes page that fetches Ozone volumes, supports limit selection, column selection, search by volume/owner/admin, and shows ACLs in a drawer.

Important APIs/types/functions: Uses `useApiData<VolumesResponse>(/api/v1/volumes?limit=...)`, `useAutoReload`, `useDebounce`, `VolumesTable`, `AclPanel`, `SingleSelect`, `MultiSelect`, and `Search`. Main handlers are `handleColumnChange`, `handleLimitChange`, `handleTagClose`, `handleAclLinkClick`, and `loadVolumesData`.

Control flow: Selected limit is included in the hook URL. Refetch is invoked by auto reload and manual reload. When volume data changes, the effect maps backend rows into `Volume` objects and updates table data plus `lastUpdated`. Search column changes clear the term. Clicking an ACL link stores the current row and opens the drawer.

State and persistence: Local state stores table data, last update, and column options. Separate state stores current ACL row, selected columns, selected limit, search column/term, and drawer visibility. There is no persistence or URL state.

Dependencies and integration points: Integrates with `/api/v1/volumes`, v2 volume and ACL types, the shared limit constants, and table/drawer components. The table calls back to `handleAclClick`.

Risks: The `currentRow` state is typed as `Volume | Record<string, never>` but rendered as though it always has `acls` and `volume`, which can produce undefined props before a row is selected. The data effect spreads stale `state` from a closure. Changing `selectedLimit` changes the hook URL, but first load still relies on `initialFetch:false` and explicit refetch behavior. It maps only known fields, so new backend fields are intentionally discarded.

Test signals: Tests should cover limit changes, reload, column selection/tag close, all three search columns, ACL drawer open/close, empty data, and fetch errors.
