# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/breadcrumbs/breadcrumbs.tsx


Purpose: Legacy breadcrumb renderer for route paths.

Important APIs/types/functions: Class `Breadcrumbs` wrapped with `withRouter`, uses `breadcrumbNameMap`, `HomeOutlined`, and `Link`.

Control flow/state/persistence: Splits `location.pathname`, builds cumulative URLs, maps them to labels, and prepends a home crumb linking to `/`.

Dependencies/integration points: Used by legacy app shell when old UI is enabled. Depends on routes and `breadcrumbNameMap` staying aligned.

Risks/test signals: Unknown paths render undefined labels. No tests directly cover breadcrumb labels in this subset.
