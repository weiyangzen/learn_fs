# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/containersTable.tsx

Purpose: Displays unhealthy/quasi-closed containers with manual cursor pagination and expandable key listings per container.

Important APIs, types, and functions: Exports `ContainerTable` and `COLUMNS`. Props include selected columns, expansion state/setter, search config, page navigation callbacks, page size, and optional unhealthy-since title.

Control flow: Filters columns and rows, maps selected container expansion to `/api/v1/containers/{id}/keys` via `fetchData`, stores fetched key rows in parent-owned `expandedRow`, renders nested key table, and draws explicit previous/next buttons.

State and persistence behavior: Expansion data lives in parent state; this component triggers updates and displays per-row loading. No persistence.

Dependencies: Uses AntD table, popover, select, buttons, `filesize`, moment utils, `fetchData`, and container types.

Integration points: Shared by the Containers page for five unhealthy tabs plus the quasi-closed tab.

Risks and edge cases: Expanded row loading is not set true before fetch in this component, so parent initialization must provide it. Search assumes string `pipelineID` or numeric `containerID`. Nested key table pagination does not use server-side paging despite total count.

Test signals: Cover row expansion success/error, manual next/previous boundaries, page-size changes from parent, search by ID/pipeline, checksum popover rendering, and alternate title for quasi-closed.
