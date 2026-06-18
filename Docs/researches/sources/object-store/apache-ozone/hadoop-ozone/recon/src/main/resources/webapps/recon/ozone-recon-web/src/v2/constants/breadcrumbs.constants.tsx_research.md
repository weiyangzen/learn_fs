# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/breadcrumbs.constants.tsx

Purpose: Maps Recon v2 route paths to breadcrumb display names.

Important APIs, types, and functions: Exports `breadcrumbNameMap` typed as path string to display string.

Control flow: Static lookup only.

State and persistence behavior: No state or persistence.

Dependencies: No imports.

Integration points: Consumed by layout/navigation breadcrumb components and includes `/Assistant` as `Recon AI`.

Risks and edge cases: Route strings must stay synchronized with `routes-v2.tsx`; missing dynamic paths or renamed routes produce blank breadcrumbs.

Test signals: Check every top-level v2 route has a breadcrumb and renamed routes update this map.
