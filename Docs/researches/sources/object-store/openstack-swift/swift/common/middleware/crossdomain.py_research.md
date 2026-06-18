# sources/object-store/openstack-swift/swift/common/middleware/crossdomain.py

## Purpose
`crossdomain.py` serves a static `/crossdomain.xml` policy document for legacy browser/plugin clients such as Flash, Java, and Silverlight. It lets operators configure the policy body inserted into a cross-domain-policy XML wrapper.

## Important APIs, Types, and Functions
`CrossDomainMiddleware.GET()` builds the XML response. `__call__()` intercepts only `GET /crossdomain.xml`. `filter_factory()` merges config, registers Swift info, and returns the filter.

## Control Flow
Initialization records the downstream app and chooses `cross_domain_policy`, defaulting to a permissive wildcard policy. Requests to `/crossdomain.xml` with method GET are answered directly with `application/xml`; all other requests pass through unchanged.

## State and Persistence
The configured policy is process-local immutable state. No request state is persisted.

## Dependencies and Integration Points
The module uses `Request`, `Response`, and `register_swift_info`. It is intended to be early in the proxy pipeline, before auth, so unauthenticated clients can fetch the policy.

## Risks and Edge Cases
The default policy is intentionally permissive and may be inappropriate for private deployments. The configured policy text is interpolated directly into XML, so malformed config yields malformed XML. Only GET is handled; HEAD or OPTIONS pass through.

## Test Signals
Tests should assert default policy output, configured multiline policy output, content type, GET-only behavior, pass-through for other paths/methods, and `/info` registration.
