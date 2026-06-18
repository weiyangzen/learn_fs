# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/breadcrumbs/breadcrumbs.tsx


Purpose: V2 hook-based route breadcrumb renderer.

Important APIs/types/functions: Default export `Breadcrumbs`, uses `useLocation`, `breadcrumbNameMap`, `HomeOutlined`, and `Link`.

Control flow/state/persistence: Splits current pathname, builds cumulative breadcrumb links, prepends home, and renders AntD `Breadcrumb`.

Dependencies/integration points: Used by `app.tsx` when new UI is active. Depends on V2 breadcrumb constants and route names.

Risks/test signals: Unknown path segments display undefined. Assistant route still participates in app header unless specially styled by app shell.
