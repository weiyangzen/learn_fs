# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/container.types.ts

Purpose: Declares v2 container, unhealthy-container pagination, key expansion, quasi-closed container, table prop, and export job types.

Important APIs/types/functions: Exports `ContainerReplica`, `Container`, `KeyResponse`, `ContainerKeysResponse`, `ContainersPaginationResponse`, `QuasiClosedContainer`, `QuasiClosedContainersResponse`, `TabPaginationState`, `ContainerTableProps`, `ExpandedRow`, `ExpandedRowState`, `ContainerState`, `ExportJobStatus`, and `ExportJob`.

Control flow: Type-only module. It models cursor/pagination state through first/last keys and page history, expanded rows keyed by container id, and export job lifecycle from queued through completed/failed.

State and persistence: No state in the module. Several types are designed to represent page-local state (`TabPaginationState`, `ContainerState`) and long-running backend export state (`ExportJob` with timestamps and remaining downloads).

Dependencies and integration points: Used by v2 containers tables/pages and row expansion against `/api/v1/containers/{id}/keys`. Imports v2 multi-select `Option` for table-column selection props.

Risks: The file has both `containerID` and `containerId` naming conventions across types, mirroring backend inconsistencies and increasing mapping mistakes. `ExportJob.state` is an unconstrained string even though `status` is constrained. `KeyResponse.Blocks` is keyed by `number`, but JSON object keys are strings at runtime.

Test signals: Fixture tests should cover all unhealthy count fields, row expansion key shapes, quasi-closed container rows, cursor pagination state transitions, and export job status rendering for queued/running/completed/failed.
