# sources/object-store/openstack-swift/swift/common/middleware/gatekeeper.py

## Purpose
`gatekeeper.py` protects Swift internal metadata and backend control headers from clients. It strips inbound private headers, strips outbound private headers, optionally shunts client `X-Timestamp` into an internal backend header, and can convert absolute Location headers to relative locations for configured flows.

## Important APIs, Types, and Functions
`inbound_exclusions` and `outbound_exclusions` define regex prefixes for account/container/object sysmeta, object transient sysmeta, and `x-backend`. `make_exclusion_test()` compiles the matcher. `GatekeeperMiddleware.__call__()` applies request filtering and response filtering. `filter_factory()` exposes the filter.

## Control Flow
For each request, `Request(env)` builds mutable headers. Matching inbound headers are removed and logged at debug. If enabled, `X-Timestamp` is moved to `X-Backend-Inbound-X-Timestamp`, preserving the value for trusted downstream middleware such as container sync while keeping direct client timestamp writes out of normal paths. If `X-Allow-Reserved-Names` is allowed, it is moved to `X-Backend-Allow-Reserved-Names`. The wrapped `start_response` optionally rewrites `Location` to relative when `swift.leave_relative_location` is set, then removes matching outbound private headers before returning to the client.

## State and Persistence
No durable state is stored. The middleware mutates request and response headers in memory and logs removed/shunted headers.

## Dependencies and Integration Points
It depends on Swift request helpers for sysmeta prefixes and header removal, `Request`, `config_true_value`, URL splitting, and regex matching. It must be early in the pipeline, immediately after `catch_errors`, so later middleware can safely use internal headers.

## Risks and Edge Cases
Regex prefixes must stay aligned with Swift internal header namespaces. Allowing reserved-name headers is a privileged compatibility mode. Relative Location rewriting preserves path, query, and fragment but drops scheme/host. Debug logs can include header names and values, so log exposure should be considered.

## Test Signals
Tests should cover inbound sysmeta/transient/backend stripping, outbound stripping, `X-Timestamp` shunting on/off, reserved-name header shunting on/off, relative Location rewriting, no-op absolute Location behavior, case-insensitive matching, and debug logging of removed headers.
