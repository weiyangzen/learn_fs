# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/duBreadcrumbNav/duBreadcrumbNav.tsx


Purpose: Namespace Usage/Disk Usage breadcrumb navigation with dropdown subpath drilldown and free-form path search.

Important APIs/types/functions: `DUBreadcrumbNav`, props `path`, `subPaths`, `updateHandler`, and local handlers for menu click, search, breadcrumb click, submenu generation, and current path state.

Control flow/state/persistence: Maintains `currPath` from `path` in state. Breadcrumb clicks construct parent paths; submenu items navigate to non-key subpaths; search appends an entered path segment.

Dependencies/integration points: Used by namespace usage pages with `NUSubpath` data from backend.

Risks/test signals: Path construction comments note double-slash edge cases handled by substring. Menu item keys rely on raw paths. Key subpaths are intentionally not drillable.
