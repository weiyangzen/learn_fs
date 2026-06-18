# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/overview.types.ts

Purpose: Defines v2 Overview dashboard response and local state types.

Important APIs/types/functions: Exports `ClusterStateResponse`, `TaskStatus`, `KeysSummary`, `StorageReport`, and `OverviewState`.

Control flow: Type-only module. `TaskStatus.taskName` includes known OM task names while allowing arbitrary strings, and `StorageReport` supports capacity-breakdown arithmetic.

State and persistence: No runtime state. `OverviewState` contains local OM sync status and refresh timestamp only.

Dependencies and integration points: Used by v2 Overview page and overview card components. Maps to `/api/v1/clusterState`, `/api/v1/task/status`, and key summary endpoints.

Risks: `ClusterStateResponse` requires all count and service-id fields, so default constants must stay complete. `KeysSummary` omits `totalOpenKeys`/`totalDeletedKeys`, causing pages to use intersections for those endpoint-specific fields. `TaskStatus.taskName` is not a discriminated union because of the catch-all `string`.

Test signals: Fixture tests should cover missing/zero counts, storage report arithmetic, known and unknown task names, and summary endpoints with additional count fields.
