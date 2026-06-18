<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/slo.py -->
# sources/object-store/openstack-swift/swift/common/middleware/slo.py

## Purpose
Implements Swift Static Large Object middleware. It lets clients store a manifest that references object segments and inline data, validates manifests on PUT, serves concatenated large objects on GET/HEAD, exposes raw/transformed manifests, supports part-number and range reads, deletes segments synchronously or asynchronously, and adjusts container listings to expose SLO ETags.

## Important APIs, types, and functions
`parse_and_validate_input` validates uploaded manifest JSON. `_annotate_segments`, `calculate_byterange_for_part_num`, and `calculate_byteranges` prepare segment metadata for reads. `RespAttrs` extracts SLO state from response headers and calculates legacy size/ETag when needed. `SloGetContext` handles GET/HEAD, manifest refetching, sub-SLO recursion, range slicing, and `SegmentedIterable` construction. `StaticLargeObject` is the WSGI middleware with handlers for multipart PUT, GET/HEAD, DELETE, async delete, segment discovery, and container listings. `filter_factory` registers cluster-visible SLO capabilities.

## Control flow
Manifest PUT enforces content length/size limits, parses JSON, validates object-backed and inline segments, HEADs each unique object path concurrently, normalizes ranges, checks size/ETag constraints, applies optional `swift.callback.slo_manifest_hook`, calculates the SLO ETag, stores JSON plus `X-Static-Large-Object`, `SYSMETA_SLO_ETAG`, `SYSMETA_SLO_SIZE`, manifest MD5 ETag, and content-type `swift_bytes`. Heartbeat mode returns early `202 Accepted` and later embeds final status in the body. GET/HEAD first asks object servers to ignore Range for manifests and to use SLO ETag sysmeta for conditionals. If needed, it refetches the full manifest, annotates segments, handles part-number and range math, recursively expands sub-SLOs to depth 10, and streams segments through `SegmentedIterable`. DELETE with `multipart-manifest=delete` walks nested manifests and uses bulk delete, or async delete when allowed and all segments are simple objects in one container.

## State and persistence behavior
Persistent state is the manifest object body plus object sysmeta `slo-etag` and `slo-size`, `X-Static-Large-Object`, and content-type `swift_bytes`. Container listings carry `slo_etag` as an ETag parameter that `handle_container_listing` exposes separately. Runtime state includes rate-limit settings, max manifest size/segments, concurrency, bulk deleter, expirer config, sub-SLO LRU cache, and response header/status captured by `WSGIContext`. Inline data is stored base64 in the manifest and decoded to `raw_data` for serving.

## Dependencies and integration points
Integrates with Swift WSGI, object-server manifest metadata, `SegmentedIterable`, bulk delete middleware, object expirer, container listings, request helper ETag/range utilities, container authorization, and proxy logging via `swift.source='SLO'`. It is also consumed by S3 multipart flows through S3 request/response handling and multipart-manifest query generation.

## Risks and test signals
High-risk areas are manifest validation edge cases, concurrent HEAD validation, legacy manifest fallback, recursive sub-SLO expansion, ranged and part-number responses, heartbeat response formatting, async delete authorization and expirer enqueueing, and content-type `swift_bytes` accounting. Tests should cover invalid JSON and schema errors, self-referential manifests, inline-only rejection, base64 normalization, object segment size/ETag/range mismatches, max segment and manifest size limits, client ETag mismatch, GET/HEAD conditionals, 206/416 part-number behavior, range slicing across inline/object/sub-SLO segments, recursion-depth failure, broken segment 409, sync and async delete restrictions, and JSON container listing ETag rewriting.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/slo.py -->
