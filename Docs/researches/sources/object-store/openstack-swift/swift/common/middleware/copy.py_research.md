# sources/object-store/openstack-swift/swift/common/middleware/copy.py

## Purpose
`copy.py` implements server-side object copy. It supports `PUT` with `X-Copy-From`, native `COPY` with `Destination`, cross-account copy headers, optional heartbeat responses, and large-object manifest copy semantics.

## Important APIs, Types, and Functions
Header validators `_check_copy_from_header()` and `_check_destination_header()` validate path-style headers. `_copy_headers()` transfers user/system/transient metadata and delete-at headers. `ServerSideCopyWebContext` performs source GET, sink PUT, heartbeat wrapping, and OPTIONS response augmentation. `ServerSideCopyMiddleware` handles method routing and request rewriting.

## Control Flow
Object requests are inspected for `PUT` plus `X-Copy-From`, `COPY`, or `OPTIONS`. `COPY` is rewritten into a destination `PUT`, moving destination account/container/object into `PATH_INFO` and setting `X-Copy-From`. `handle_PUT()` rejects request bodies, optionally enables heartbeat flushing, resolves source account and path, fetches the source with `X-Newest`, refuses chunked or too-large source objects, builds a sink request preserving environment, copies metadata according to `x-fresh-metadata`, adjusts multipart-manifest and version-id params, streams source app_iter as sink `wsgi.input`, and adds copied-from response headers.

## State and Persistence
No local state is persisted. The destination object and metadata are persisted by the downstream PUT. Source app iterators are explicitly closed after streaming.

## Dependencies and Integration Points
It depends on `make_subrequest`, `WSGIContext`, `FileLikeIter`, Swift request helper metadata predicates, account format checks, `MAX_FILE_SIZE`, eventlet heartbeat spawning, and heartbeat response body generation. Pipeline placement is after auth and before quotas and large-object middleware so authorization and size policies apply correctly.

## Risks and Edge Cases
Pipeline order is critical: if copy runs on the wrong side of encryption or large-object middleware, stored crypto metadata or manifest behavior can be wrong. Source responses without `Content-Length` are refused. Partial/ranged copies intentionally omit source ETag validation. Heartbeat mode returns `202 Accepted` while the true copy status is embedded later in the body. Metadata copying must avoid backend/private headers and container-update override leakage.

## Test Signals
Tests should cover both COPY styles, cross-account headers, malformed source/destination headers, zero-body enforcement, source error propagation, max-size refusal, heartbeat success and error bodies, metadata preservation and `x-fresh-metadata`, SLO/DLO manifest parameter handling, version-id stripping, copied-from response headers, OPTIONS Allow/CORS augmentation, and iterator cleanup.
