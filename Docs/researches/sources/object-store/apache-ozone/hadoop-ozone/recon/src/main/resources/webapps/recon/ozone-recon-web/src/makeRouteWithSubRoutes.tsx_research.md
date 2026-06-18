# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/makeRouteWithSubRoutes.tsx


Purpose: Shared route factory for legacy and V2 route arrays.

Important APIs/types/functions: Exports `MakeRouteWithSubRoutes(route: IRoute)`, returning a React Router `Route` that renders `route.component` with router props and `routes={route.routes}`.

Control flow/state/persistence: Stateless functional renderer. Route matching uses the `path` supplied by each route object and is not `exact`.

Dependencies/integration points: Used by `app.tsx` when mapping `routes` and `routesV2`; depends on `IRoute`.

Risks/test signals: Non-exact matching can allow broader route matches depending on order. Component type is dynamically rendered as `<route.component>`, which is valid but relies on route objects being well-formed.
