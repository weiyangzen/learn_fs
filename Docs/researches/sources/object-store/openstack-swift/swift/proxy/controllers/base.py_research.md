# sources/object-store/openstack-swift/swift/proxy/controllers/base.py

## Purpose
This module is the shared foundation for Swift proxy controllers. It converts backend headers into cacheable info dictionaries, manages account/container/object info caches, provides CORS and authorization-delay decorators, implements backend GET/HEAD source selection and failover, yields ring nodes with handoff/error-limit handling, and supplies controller fan-out/quorum response logic.

## Important APIs, Types, and Functions
Header/info helpers include `update_headers()`, `_prep_headers_to_info()`, `headers_to_account_info()`, `headers_to_container_info()`, `headers_from_container_info()`, and `headers_to_object_info()`. Cache helpers include `get_account_info()`, `get_container_info()`, `get_object_info()`, `get_info()`, `get_cache_key()`, `set_info_cache()`, `set_object_info_cache()`, `clear_info_cache()`, `_get_info_from_infocache()`, `_get_info_from_memcache()`, `_get_info_from_caches()`, and `record_cache_op_metrics()`. Shard namespace cache helpers include `namespace_bounds_to_list()`, `namespace_list_to_bounds()`, `get_namespaces_from_cache()`, and `set_namespaces_in_cache()`.

Request/response helpers include `delay_denial`, `cors_validation`, `_prepare_pre_auth_info_request()`, `close_swift_conn()`, `bytes_to_skip()`, `is_good_source()`, and `is_useful_response()`. Streaming and source-selection types include `ByteCountEnforcer`, `GetterSource`, `GetterBase`, and `GetOrHeadHandler`. `NodeIter` yields primary and handoff nodes while respecting error limiting. `Controller` is the base class used by account, container, object, and info controllers.

## Control Flow
Info lookup first checks `env['swift.infocache']`, then memcache unless skipped, then makes a pre-authorized HEAD subrequest when allowed. Account and container info cache entries are normalized into dictionaries and type-coerced before returning; object info is only cached per request. Container info lookup also verifies account existence unless the account is auto-createable and may include bytes from a versions container.

`GetOrHeadHandler.get_working_response()` repeatedly finds a suitable backend source with `_find_source()`. `_make_node_request()` connects to nodes, records successful sources, filters stale object copies behind tombstones, suppresses some handoff 404/5xx responses, and tracks latest 404 timestamps. For object GETs without `x-newest`, read failures can fast-forward the Range header and replace the source to resume from another node with the same ETag. Multipart/range responses are converted into response body iterators and backend sockets are forcibly closed on completion.

`Controller.make_requests()` runs backend requests concurrently using `GreenAsyncPile`, stops when quorum is reached, waits briefly for post-quorum responses, fills missing responses with 503 stubs, and returns `best_response()`. `best_response()` chooses the strongest quorum class among 2xx, 3xx, and 4xx groups, applies optional status overrides, and falls back to 503 with logging. `OPTIONS()` implements CORS preflight support. Listing helper methods fetch and parse JSON container listings and convert shard records to `Namespace` objects.

## State and Persistence Behavior
This file manages request-scoped `swift.infocache` and optional memcache entries for account/container info and shard namespace bounds. It does not directly persist storage data; it influences backend persistence through generated request headers and fan-out methods. It mutates backend Range headers during GET resume, response headers during cache/header conversion, and node timing/error state through `app` callbacks. Cache TTLs are controlled by backend recheck headers or defaults.

## Dependencies and Integration Points
It is deeply integrated with Swift's WSGI request helpers, memcache abstraction, ring/node selection, buffered HTTP client, storage policies, CORS config, request metadata helpers, namespace/sharding utilities, and swob response classes. Controllers depend on app-provided settings such as timeouts, concurrency, request node counts, CORS allowlists, cache skip probabilities, error limiting, backend user agent, and policy options.

## Risks and Edge Cases
Cache correctness is central: stale account/container info can change authorization, object versioning byte counts, sharding decisions, and write preconditions. Cache skip/error states must be accurately recorded for observability. GET resume logic must not switch between different object versions; the saved ETag guard is critical. Handoff 404 handling avoids false negatives during rebalance but can delay authoritative errors. `cors_validation()` assumes `cors_info['allow_origin']` exists when an Origin is present; malformed container info would be risky. `set_namespaces_in_cache()` rejects `shard-updating` keys because updating caches use a different cooperative path.

## Test Signals
Targeted tests should cover header-to-info normalization, metadata/sysmeta stripping, cache hit/miss/skip/error behavior, negative cache TTL scaling, object info request-only caching, namespace cache round trips, CORS simple and preflight responses, `bytes_to_skip()`, `ByteCountEnforcer` short-read errors, GET source failover and Range rewriting, tombstone/newest selection, NodeIter handoff logging, quorum grouping/overrides, and owner-only preauth info request behavior.
