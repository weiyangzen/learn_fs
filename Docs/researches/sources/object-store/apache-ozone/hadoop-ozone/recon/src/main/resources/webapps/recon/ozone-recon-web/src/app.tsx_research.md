# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/app.tsx


Purpose: Top-level React app shell that chooses legacy vs V2 navigation/routes, owns sidebar collapse and UI-version preference, and wraps the route switch in a hash router.

Important APIs/types/functions: `IAppState`, functional `AppLayout`, class `App`, `onCollapse`, and `onToggleUI` callback. Uses `routes`, `routesV2`, `MakeRouteWithSubRoutes`, legacy/V2 navbars and breadcrumbs, AntD `Layout` and `Switch`.

Control flow/state/persistence: `App` initializes `collapsed: false` and `enableOldUI` from `sessionStorage`. Toggle writes `enableOldUI` back to session storage. Root `/` redirects to `/Overview`; unknown routes render V2 `NotFound`.

Dependencies/integration points: Integrates with `HashRouter`, route arrays, Suspense `Loader`, and special Assistant layout/footer suppression.

Risks/test signals: `AppLayout` props are `any`; route switch mixes legacy and V2 not-found behavior. Session storage JSON parsing can throw if corrupted.
