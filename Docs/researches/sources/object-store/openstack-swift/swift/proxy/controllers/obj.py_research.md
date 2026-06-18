# sources/object-store/openstack-swift/swift/proxy/controllers/obj.py

## Purpose

`obj.py` implements Swift proxy object request handling. It routes object operations to either replicated or erasure-coded storage-policy controllers, performs authorization-delayed request validation, fans out PUT/POST/DELETE requests to object servers and container-update targets, reconstructs EC GET responses, and hides backend implementation details from clients.

## Important APIs and Types

`check_content_type` rejects client `Content-Type` parameters beginning with `swift_` unless middleware intentionally overrode the header. `num_container_updates` computes how many object-server requests need container-update headers so successful object writes also make durable container listings.

`ObjectControllerRouter` maps storage policy types to concrete object controllers using class registration. `BaseObjectController` owns shared GET/HEAD/PUT/POST/DELETE setup: it resolves container info, policy and object ring, validates ACLs and object metadata, handles object expiration headers, computes container/shard update targets, constructs backend headers, opens PUT connections, collects backend responses, and delegates policy-specific data transfer.

`ReplicatedObjectController` handles replicated storage policies. It reads client bytes once and writes each chunk to all successful `Putter` connections, requires replica quorum, verifies consistent backend ETags, and returns the best backend response.

`ECObjectController` handles erasure-coded policies. Its GET path widens client ranges to EC segment/fragment ranges, collects fragment responses into timestamp buckets, selects a durable reconstructible bucket, and returns an `ECAppIter` that decodes fragments into client bytes. Its PUT path encodes client chunks into EC fragments, streams each fragment to the chosen node/frag index, sends EC metadata footers, waits for first-phase acknowledgements, then sends a multiphase commit confirmation.

`Putter` wraps a backend PUT connection, state machine, timeout handling, chunked transfer framing, and final response collection. `MIMEPutter` extends it for metadata footers and multiphase EC commits. `chunk_transformer`, `trailing_metadata`, `client_range_to_segment_range`, and `segment_range_to_fragment_range` are the key pure helpers for EC PUT/GET conversion. `ECGetResponseBucket`, `ECGetResponseCollection`, and `ECFragGetter` coordinate EC GET fragment discovery, alternate-node hints, retry/fast-forward behavior, and response-part iteration.

## Control Flow

GET and HEAD resolve the container, storage policy, object ring partition, and a `NodeIter`, then call the policy controller's `_get_or_head_response`. Replicated GET/HEAD delegates to the shared `GETorHEAD_base`; EC HEAD also uses that path but fixes EC headers, while EC GET starts concurrent fragment GETs, groups responses by data timestamp, requests extras or alternates until it has enough durable fragments, builds an `ECAppIter`, and fixes conditional/range/client-visible headers.

PUT validates `If-None-Match`, container existence, metadata, content type, request size, expiration headers, and container-update headers. Shared code opens object-server connections with `Expect: 100-continue`. Replicated PUT streams identical chunks to all active putters and needs replica quorum. EC PUT removes client `Content-Length`/ETag from backend headers, calculates expected fragment archive size when possible, erasure-encodes full segments through `chunk_transformer`, writes per-frag metadata footers, enforces quorum on the first phase, and sends commit confirmations before collecting final durable responses.

POST sends metadata updates to primaries, detects mixed accepted/not-found results, and may retry missing primaries on handoffs before computing the best response. DELETE computes write-affinity local handoff counts when enabled, sets container-update headers, and treats backend 404s as client 204s through status overrides.

## State and Persistence

The controller itself is request-scoped and persists no durable local state. Durable effects are remote: object data files, EC fragment archives, durable marker files, object metadata, container database updates, async-pending container updates, and expirer queue updates are written by backend servers. In-memory state includes shard-update namespace cache data in request infocache/memcache, per-request putter state, EC response buckets, timeout/watchdog state, and logger thread locals.

## Dependencies and Integration Points

The file depends on Swift's common concurrency primitives, HTTP helpers, constraints, storage policies, swob responses, request helpers, and base proxy controller machinery. It integrates with container info lookups, object rings, container rings, expirer config, memcache-backed shard-range caching, object-server multipart footer support, PyECLib EC drivers, middleware footer callbacks, authorization hooks, CORS/delay-denial decorators, and backend node error limiting exposed by the proxy `Application`.

## Risks and Edge Cases

The highest-risk areas are EC range conversion and reconstruction, because suffix and multipart ranges must be widened to fragments then trimmed back exactly. EC GET bucket selection must avoid mixing timestamps or mismatched EC ETags, and must not serve non-durable fragments as complete objects. PUT streaming must handle client disconnects, slow clients, backend write failures, `If-None-Match` races, oversized bodies, mismatched ETags, and quorum response timing. Container update durability depends on the quorum math in `num_container_updates` and on correct shard target selection/caching. MIME multipart support depends on backend capability negotiation; old or partial deployments can surface as footer or multiphase support failures. The file mutates request headers such as `Range`, `Content-Length`, and EC sysmeta exposure, so ordering of `_fix_ranges`, `kickoff`, and `_fix_response` matters.

## Test Signals

Important tests should cover content-type rejection, container update count math, shard-update cache hit/miss/disabled behavior, PUT quorum and failure paths, replicated ETag mismatch, object expiration headers, POST mixed 202/404 handoff behavior, DELETE write-affinity handoff selection, EC client-range to segment/fragment conversions, EC GET bucket/tombstone/durable selection, EC GET alternate-node injection, EC multipart and suffix range responses, EC PUT footer metadata and commit phases, client timeout/disconnect handling, and backend capability negotiation for MIME footers/multiphase commits.
