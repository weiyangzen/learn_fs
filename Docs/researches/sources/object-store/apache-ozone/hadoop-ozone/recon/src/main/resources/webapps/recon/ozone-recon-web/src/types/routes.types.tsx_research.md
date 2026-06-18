# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/types/routes.types.tsx


Purpose: Shared route object type.

Important APIs/types/functions: Exports `IRoute` with `path`, `component: React.ElementType`, and optional nested `routes`.

Control flow/state/persistence: None; type definition only.

Dependencies/integration points: Used by `routes.tsx`, V2 route tables, and `MakeRouteWithSubRoutes`.

Risks/test signals: It does not model route exactness, guards, labels, or sidebar metadata, so route behavior lives outside the type.
