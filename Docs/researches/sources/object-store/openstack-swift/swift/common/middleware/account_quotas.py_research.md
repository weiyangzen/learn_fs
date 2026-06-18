# sources/object-store/openstack-swift/swift/common/middleware/account_quotas.py

Purpose: WSGI middleware that lets reseller requests set account-wide and per-storage-policy byte/object quotas, exposes those quotas as account headers, and blocks non-reseller object PUTs that would exceed them.

Important APIs/types/functions: `AccountQuotaMiddleware.quota_exceeded` returns or defers a 413 response; `validate_and_translate_quotas` validates user-facing quota headers and maps them to account sysmeta; `handle_account` manages quota header translation and response exposure; `__call__` parses request paths and enforces quotas; `filter_factory` registers Swift info and returns the paste filter.

Control flow: account PUT/POST requests first translate legacy `X-Account-Meta-Quota-Bytes`, validate global and per-policy quota bytes/count headers, require `reseller_request` for any quota mutation, and write sysmeta headers. Account responses copy sysmeta quotas back to user-visible headers. For object PUTs, reseller requests bypass enforcement. Other requests fetch account info, check global bytes and count quotas using current aggregate stats plus incoming content length/default one object, fetch container info for storage policy, then check per-policy bytes and count. When a quota is exceeded and authorization is delayed, `quota_exceeded` wraps `swift.authorize` so normal auth still runs before returning 413.

State and persistence: quotas persist as account sysmeta, while enforcement reads eventually consistent account and storage-policy counters. No local durable state.

Dependencies and integration: uses Swift `swob` HTTP exceptions and `wsgify`, storage `POLICIES`, registry `register_swift_info`, and proxy controller `get_account_info`/`get_container_info`. Intended placement is after auth middleware and before proxy-server.

Risks: eventual consistency can allow temporary over-quota writes; uploads without content length only compare current usage plus zero bytes; per-policy quotas are independent of global quota; malformed stored quotas are treated as disabled; delayed authorization wrapping must preserve auth semantics. Tests should cover reseller/non-reseller quota updates, legacy header translation, quota removal dominance, response exposure, object PUT global and per-policy byte/count rejection, missing account/container info pass-through, and delayed-authorize behavior.
