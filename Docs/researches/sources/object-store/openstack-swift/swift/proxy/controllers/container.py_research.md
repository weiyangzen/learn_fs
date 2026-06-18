# sources/object-store/openstack-swift/swift/proxy/controllers/container.py

## Purpose
This module implements the proxy controller for container-level requests. It handles container metadata and ACL operations, storage-policy selection, account existence checks, container info cache invalidation, sharded-container listing assembly, shard namespace caching, and internal bulk `UPDATE` forwarding.

## Important APIs, Types, and Functions
`ContainerController` extends `Controller` with `server_type = 'Container'` and passes through container ACL, sync, and versions headers. Key helpers are `_convert_policy_to_index()`, `clean_acls()`, `_clear_container_info_cache()`, `_GETorHEAD_from_backend()`, `_filter_complete_listing()`, `_get_listing_namespaces_from_cache()`, `_set_listing_namespaces_in_cache()`, `_get_listing_namespaces_from_backend()`, `_record_shard_listing_cache_metrics()`, `_GET_auto()`, `_get_or_head_pre_check()`, `_get_or_head_post_check()`, `_get_from_shards()`, and `_backend_requests()`. Public methods are `GET()`, `HEAD()`, `PUT()`, `POST()`, `DELETE()`, plus private `UPDATE()`.

## Control Flow
GET validates listing parameters, checks account existence and authorization preconditions, forces JSON format, then either goes directly to container servers for explicit `object`/`shard` record requests or calls `_GET_auto()` for client-style listings. `_GET_auto()` attempts to use cached shard namespaces when the container is known sharded and cache is enabled; otherwise it asks the backend for `auto` records with namespace format. Successful complete namespace responses for sharded containers are compacted into `NamespaceBoundList` and cached. When namespaces are available, `_get_from_shards()` recursively fetches object listings from shard containers, prevents loops through request history, preserves root storage policy, applies marker/end-marker/reverse/prefix constraints, stops at limit, and may update object-count/bytes headers for unconstrained complete listings.

HEAD performs account precheck, backend HEAD, and postcheck. PUT cleans ACLs and metadata, converts `X-Storage-Policy` to a backend policy index, hides owner-only headers from non-owners, maps reseller `X-Container-Sharding` to sysmeta, checks container-name length, autocreates missing accounts when configured, enforces per-account container limits, builds account update headers, sends container PUTs, and clears caches. POST updates metadata after account existence validation. DELETE sends container DELETEs and maps 202 Accepted to 404 when no server had the container. Private UPDATE forwards request bodies to container servers for internal merge-style operations using a caller-supplied storage policy index.

## State and Persistence Behavior
Persistent effects happen on account/container servers, not locally. The controller mutates request headers for backend policy, sharding, record type, and account update information. It clears container metadata and listing namespace cache entries on writes/deletes/posts. It can populate container info cache after successful reads and namespace caches for complete sharded listings. Shard listing history is request-scoped in `swift.shard_listing_history`.

## Dependencies and Integration Points
It integrates with base controller fan-out, account/container rings, storage policy registry, metadata and listing parameter validators, ACL cleaners from middleware, namespace cache helpers, container sharder semantics, listing format middleware, app settings for shard cache recheck/skip, max containers per account, account autocreate, and owner/reseller request flags.

## Risks and Edge Cases
Shard listings are the most complex area: stale namespace caches can omit or duplicate objects, policy mismatches abort listings, loops must be forced to object listings, and misplaced objects around namespace bounds require careful marker/end-marker handling. Container limit enforcement must allow existing containers while blocking new ones. `PUT` must reject deprecated or unknown storage policies. Cache invalidation currently does not purge updating-shard caches, noted by a TODO. Private UPDATE trusts backend headers and must remain gated by private-method authorization outside this file.

## Test Signals
Tests should cover policy name conversion and deprecated policies, ACL cleaning, cache clearing on mutations, auto vs explicit record-type GET paths, namespace cache hit/miss/force-skip/disabled metrics, shard listing recursion and loop prevention, policy mismatch 503, marker/end-marker/reverse/prefix behavior, object count inference, account autocreate on PUT, max-container limit enforcement, owner/reseller header handling, DELETE 202-to-404 mapping, and private UPDATE body fan-out.
