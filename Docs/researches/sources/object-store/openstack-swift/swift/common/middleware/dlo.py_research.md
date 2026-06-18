# sources/object-store/openstack-swift/swift/common/middleware/dlo.py

## Purpose
`dlo.py` implements Dynamic Large Object support. It validates DLO manifest headers on PUT and, on GET/HEAD of manifest objects, dynamically lists segment objects and streams them as one logical object.

## Important APIs, Types, and Functions
`GetContext` handles manifest GET/HEAD. Key methods are `_get_container_listing()`, `_segment_listing_iterator()`, `get_or_head_response()`, and `handle_request()`. `DynamicLargeObject` stores rate-limit and timeout config, migrates old proxy config settings, validates `X-Object-Manifest`, and exposes the WSGI entry point.

## Control Flow
For object GET/HEAD without `multipart-manifest=get`, `GetContext` first calls downstream and checks for `X-Object-Manifest`. Manifest responses are closed, optionally drained, and replaced with a generated response. The manifest value is split into segment container and prefix. The middleware lists segment objects using container GET subrequests with prefix and marker, computes content length and aggregate ETag when the listing is complete, handles single byte ranges when enough listing data is available, and builds a `SegmentedIterable` over segment paths. PUT requests only validate that `X-Object-Manifest` has `container/prefix` form without query separators or leading slash in prefix.

## State and Persistence
DLO manifests are persisted as object metadata by normal Swift PUT/POST flows. This middleware keeps only request-local segment listings and iterators. Config values are process-local.

## Dependencies and Integration Points
It depends on container listings, `SegmentedIterable`, `RateLimitedIterator`, `make_subrequest`, `load_app_config`, Swift constraints, range helpers, MD5 ETag construction, and object response headers. It integrates with copy and SLO behavior through `multipart-manifest=get` conventions.

## Risks and Edge Cases
Incomplete listings prevent full length/ETag calculation and can cause range requests to be ignored. Listing or segment errors after response streaming starts can only close the connection via exceptions. Manifest objects whose names match their own prefix can include their own body as a segment. Segment integrity is based on response headers rather than manifest-declared size/hash. Large listings and high segment counts are rate-limited to protect backends.

## Test Signals
Tests should cover manifest PUT validation, pass-through on non-manifest GET/HEAD, complete and paged segment listings, aggregate content length and ETag, satisfiable/unsatisfiable/ignored ranges, segment iterator marker progression, listing failure before and during streaming, first-segment validation failures, rate limiting, old config migration, and `multipart-manifest=get` bypass.
