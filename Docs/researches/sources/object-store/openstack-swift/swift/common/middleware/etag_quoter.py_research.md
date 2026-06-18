# sources/object-store/openstack-swift/swift/common/middleware/etag_quoter.py

## Purpose
`etag_quoter.py` conditionally makes object response ETag headers RFC-compliant by double-quoting bare ETags. The behavior can be enabled globally, at account level, or at container level, with container settings overriding account settings.

## Important APIs, Types, and Functions
`EtagQuoterMiddleware.__call__()` handles both metadata translation on account/container requests and ETag quoting on object responses. `filter_factory()` registers `etag_quoter` info with the `enable_by_default` value.

## Control Flow
The middleware parses Swift API paths. Account or container PUT/POST-style requests translate client headers such as `X-Account-Rfc-Compliant-Etags` into sysmeta headers, and translate sysmeta response headers back to client-visible names. Object requests fetch container info; if it has no `rfc-compliant-etags` sysmeta, account info is fetched; if neither has a flag, config default is used. When enabled, the middleware calls the downstream app, scans response headers, and wraps any ETag that is not already quoted or weak-quoted.

## State and Persistence
The enablement flags are persisted as account/container sysmeta via normal metadata writes. The middleware keeps only config in memory and mutates request/response headers.

## Dependencies and Integration Points
It depends on API-version validation, container/account info lookup, `config_true_value`, and Swift registry. It must run after cache so info lookups are available and before clients see object responses.

## Risks and Edge Cases
Only object response ETags are quoted; metadata translation paths must avoid exposing sysmeta. Empty client metadata values and `X-Remove-...` clear sysmeta. If info lookups fail, object responses pass through unmodified. Quoting weak ETags is avoided when already in `W/"..."` form.

## Test Signals
Tests should cover account and container client-to-sysmeta translation, remove header behavior, response sysmeta-to-client translation, config default enablement, container override over account flag, failed info lookup pass-through, already quoted and weak quoted ETags, bare ETag quoting, non-Swift pass-through, and registry data.
