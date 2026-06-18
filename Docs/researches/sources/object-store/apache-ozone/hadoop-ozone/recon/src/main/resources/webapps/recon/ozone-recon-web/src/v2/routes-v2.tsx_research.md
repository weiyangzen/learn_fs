# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/routes-v2.tsx

Purpose: Defines the lazy-loaded route table for the v2 Recon UI.

Important APIs/types/functions: Imports `lazy` from React, creates lazy component factories for Overview, Volumes, Buckets, Datanodes, Pipelines, NamespaceUsage, Containers, Insights, OMDBInsights, Capacity, Heatmap, and Assistant, and exports `routesV2`.

Control flow: There is no runtime control flow beyond lazy import resolution when a route is matched by the app shell. Each route object has a capitalized path and component reference.

State and persistence: Stateless module. Lazy imports are cached by the bundler/runtime after load; no application state is held here.

Dependencies and integration points: Consumed by the v2 router/shell. It is the integration surface tying route URLs such as `/Overview`, `/Om`, and `/Heatmap` to page modules.

Risks: Paths are case-sensitive in common router configurations and must match all `Link` targets. There is no explicit catch-all route in this file. Adding a page requires adding both the lazy import and route object. Lazy loading requires a Suspense boundary in the consuming app.

Test signals: Route tests should verify every route path renders the expected lazy component and that existing navigation links use matching path casing.
