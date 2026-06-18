# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/buckets/buckets.tsx

Purpose: Top-level Buckets page that fetches bucket inventory, builds volume filters, manages visible columns/limit/search, and opens ACL details.

Important APIs, types, and functions: Exports default `Buckets`. Local helpers build volume-to-bucket maps and selected-volume bucket lists.

Control flow: Uses `/api/v1/buckets?limit=...`, normalizes bucket response rows, builds volume options, seeds selected volumes from URL query or all volumes, applies debounced search, and renders `BucketsTable` plus `AclPanel`.

State and persistence behavior: Tracks table metadata, selected columns/volumes/limit, search term/column, ACL panel visibility, and current row. Auto-reload state persists globally through `useAutoReload`.

Dependencies: Uses React Router `useLocation`, moment, `AutoReloadPanel`, `AclPanel`, `Search`, `MultiSelect`, `SingleSelect`, `BucketsTable`, `useApiData`, `useDebounce`, and `useAutoReload`.

Integration points: Receives `/Buckets?volume=...` links from Volumes table and talks to bucket API plus ACL drawer.

Risks and edge cases: The reviewed source contains a duplicated/nested `useEffect(() => {` near initial volume handling, which appears syntactically suspicious. State updates spread stale `state` in some handlers. Selected volume defaults can conflict with URL-seeded selection after data arrives.

Test signals: Compile/typecheck this file, then test URL volume seeding, all-volumes default, limit refetch, auto-reload, ACL drawer data, volume filter search/select-all, and table search by bucket/volume.
