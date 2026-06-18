# sources/object-store/rustfs/crates/security-governance/src/admin_matrix.rs

## Purpose
Models admin/public route authorization contracts and validates a route matrix. It provides const-friendly route specs that can be assembled statically and checked for empty paths, empty admin actions, and duplicate method/path pairs.

## Important APIs and Types
`HttpMethod` enumerates DELETE, GET, HEAD, POST, PUT with `as_str`. `AdminActionRef` wraps a static action string. `PublicRouteKind` classifies allowed public endpoints such as console assets, health, OIDC bootstrap, and STS form post. `RouteRiskLevel` classifies normal, sensitive, and high-risk routes. `AdminRouteAccess` distinguishes `AdminAction` from `Public` and exposes `admin_action`/`public_kind`. `AdminRouteSpec` stores method, path, access, and risk level with `admin`, `public`, and getter constructors.

`AdminRouteMatrixError` reports `EmptyPath`, `EmptyAdminAction`, and `DuplicateRoute`. `validate_admin_route_specs` iterates in order, trims path/action strings, and uses a `BTreeSet<(HttpMethod, &'static str)>` as the uniqueness index.

## Control Flow and State
There is no persistence or runtime mutable state beyond the local set inside validation. The API is entirely synchronous and works with borrowed static route specs.

## Integration Points
The module is re-exported by `security-governance/src/lib.rs` for admin route inventory code to consume. It likely backs control-plane route authorization audits or compile-time route manifest checks.

## Risks
Duplicate detection is exact on the literal path string and method; it does not normalize slashes, case, path parameters, or equivalent route patterns. Public routes do not require special validation beyond non-empty path. `AdminActionRef` permits any non-empty static string, so action existence must be validated elsewhere.

## Test Signals
Unit tests cover valid admin/public specs, duplicate method/path rejection, empty path rejection, and empty admin action rejection.
