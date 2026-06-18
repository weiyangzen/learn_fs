# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/namespaceUsage/namespaceUsage.tsx

Purpose: Functional v2 Namespace Usage page that visualizes size distribution under the current Ozone path and shows metadata for the selected path.

Important APIs/types/functions: Uses `useApiData<NUResponse>` for `/api/v1/namespace/usage?path=...&files=true&sortSubPaths=true`, `NUPieChart`, `NUMetadata`, `DUBreadcrumbNav`, `SingleSelect`, and local `LIMIT_OPTIONS`. Important handlers are `loadData` and `handleLimitChange`.

Control flow: The page starts at `/` with display limit `10`. Changing the breadcrumb path or clicking reload updates `currentPath`, which changes the hook URL. A side effect inspects `duResponse.status` and emits an error for `PATH_NOT_FOUND` or info notification for `INITIALIZING`. Rendering always shows an informational alert, breadcrumb/reload controls, a limit selector, the pie chart, and metadata panel.

State and persistence: Local state tracks selected limit and current path. There is no persistent storage or polling. Reloading the current path calls `loadData(duResponse.path)`, which may be a no-op if the path string is unchanged and the hook does not refetch on same URL.

Dependencies and integration points: Integrates with Recon namespace usage API, v2 namespace usage types, breadcrumb navigation, pie chart, metadata component, and shared notification helpers.

Risks: Path is interpolated without URL encoding. Reload via setting the same state value may not force a refetch depending on hook internals. Status handling notifies but does not replace stale data with an error view. `LIMIT_OPTIONS` only affects display in `NUPieChart`; it is not sent to the backend.

Test signals: Tests should cover initial root fetch, breadcrumb path changes, `PATH_NOT_FOUND` and `INITIALIZING` statuses, limit selection passed as a number, and reload semantics for same-path refresh.
