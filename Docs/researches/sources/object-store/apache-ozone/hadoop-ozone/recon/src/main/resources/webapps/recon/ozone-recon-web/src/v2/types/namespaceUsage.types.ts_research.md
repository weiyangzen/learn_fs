# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/namespaceUsage.types.ts

Purpose: Defines v2 namespace usage response and pie chart data types.

Important APIs/types/functions: Exports `NUSubpath`, `NUResponse`, and `PlotData`.

Control flow: Type-only module. `NUResponse.status` determines page notifications and error paths; `subPaths` drives breadcrumb and chart content.

State and persistence: No state. `PlotData` represents derived chart slices with display strings for size and percentage.

Dependencies and integration points: Used by Namespace Usage page, pie chart, metadata, and breadcrumb components. Mirrors `/api/v1/namespace/usage` response fields.

Risks: `status` is plain `string`, so known statuses such as `PATH_NOT_FOUND` and `INITIALIZING` are not type-checked. `sizeDirectKey` exists in the response but is not used by the v2 page. Paths must be normalized by backend or breadcrumb/chart path logic can misbehave.

Test signals: Fixtures should include root, directory, key, empty, `PATH_NOT_FOUND`, and `INITIALIZING` responses, including mixed `isKey` values.
