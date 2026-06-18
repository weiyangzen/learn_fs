# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/containerMismatchTable.tsx

Purpose: Shows containers that exist in OM or SCM but are missing from the other service, with limit, search, and existence-side filter controls.

Important APIs, types, and functions: Exports `ContainerMismatchTable`. Props provide table pagination, current limit, limit handler, expanded row renderer, and expand callback.

Control flow: Builds `/api/v1/containers/mismatch?limit=...&missingIn=...`, debounces container-ID search, refetches when limit or missing side changes, and renders expandable rows supplied by the parent.

State and persistence behavior: Local `data`, `searchTerm`, and `missingIn`. API loading/error/data is held by `useApiData`.

Dependencies: Uses AntD dropdown/menu/popover/table/tooltip, `SingleSelect`, `Search`, `useDebounce`, `useApiData`, and insights types.

Integration points: Used inside the Insights page where expanded rows typically show mismatched keys.

Risks and edge cases: The menu label says `Exists At` while state variable is `missingIn`, and the click handler inverses the clicked key. `initialFetch: false` plus refetch effect depends on hook behavior and can produce rejected promises without local catch.

Test signals: Test OM/SCM toggle URL semantics, limit changes, expansion callbacks, empty-data disabled search, debounced ID filtering, and error toast path.
