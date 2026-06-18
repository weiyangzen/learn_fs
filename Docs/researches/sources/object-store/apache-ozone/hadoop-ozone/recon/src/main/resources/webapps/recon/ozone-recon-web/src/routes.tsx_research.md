# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/routes.tsx


Purpose: Legacy route table for old Recon UI pages.

Important APIs/types/functions: Exports `routes: IRoute[]` mapping path strings to legacy view components: Overview, Datanodes, Volumes, Buckets, Pipelines, Insights, Om, MissingContainers, DiskUsage, Containers, Heatmap, and NotFound.

Control flow/state/persistence: No state; route order drives React Router matching when old UI is enabled.

Dependencies/integration points: Used by `app.tsx` through `MakeRouteWithSubRoutes`, and aligned with legacy navbar and breadcrumbs.

Risks/test signals: `/:NotFound` catch-all inside the array can interact with non-exact routing. `/Containers` currently maps to `MissingContainers`, indicating either reuse or naming drift.
