# sources/object-store/openstack-swift/swift/common/middleware/container_quotas.py

## Purpose
`container_quotas.py` enforces simple per-container byte and object-count quotas configured as container metadata. It blocks object PUTs that would exceed `X-Container-Meta-Quota-Bytes` or `X-Container-Meta-Quota-Count`, and validates quota metadata when users set it.

## Important APIs, Types, and Functions
`ContainerQuotaMiddleware` is the WSGI middleware. `bad_response()` re-runs write authorization before returning `413`, preventing unauthenticated users from learning quota-protected container existence. `filter_factory()` registers `container_quotas` in Swift info and returns the filter.

## Control Flow
The middleware parses requests as account/container/object paths. Container `PUT` or `POST` requests validate quota headers are digit strings. Object `PUT` requests fetch container info through `get_container_info(..., swift_source='CQ')`; if the container cannot be confirmed, the request passes through for normal handling. It compares cached `bytes` plus request `Content-Length` against the bytes quota, and cached `object_count` plus one against the count quota. Exceeding either quota returns `bad_response()`.

## State and Persistence
Quota values are persisted as container metadata by normal Swift metadata writes. This middleware only reads cached container info and mutates no local state.

## Dependencies and Integration Points
It depends on `get_container_info`, `is_success`, `swift.authorize`, and Swift metadata naming conventions. It should run after auth so `swift.authorize` exists and before object writes reach storage.

## Risks and Edge Cases
Quota checks are eventually consistent because container stats and cache may lag. Chunked uploads with unknown content length are treated as zero for the request, so they cannot be rejected up front for byte quota. Count quota assumes every PUT creates one new object and does not distinguish overwrites. Invalid metadata values already stored in containers are ignored rather than enforced.

## Test Signals
Tests should cover valid and invalid quota metadata updates, byte quota enforcement, count quota enforcement, auth-leak prevention via `bad_response()`, pass-through on missing or failed container info, chunked/unknown-length behavior, overwrites, and stale metadata/stat scenarios.
