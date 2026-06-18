# sources/object-store/openstack-swift/swift/common/middleware/bulk.py

## Purpose
`bulk.py` implements the Swift bulk operations middleware. It turns a single client request into many internal subrequests for two features: archive extraction with `PUT ?extract-archive=<tar|tar.gz|tar.bz2>` and bulk deletion with `POST` or `DELETE ?bulk-delete`. It deliberately returns an outer `200 OK` for accepted bulk workflows and reports true operation status in a heartbeat response body formatted as text, JSON, or XML.

## Important APIs, Types, and Functions
`CreateContainerError` carries failed auto-container creation status. `pax_key_to_swift_header()` maps tar pax extended attributes for `user.mime_type` and `user.meta.*` into object headers. `Bulk` is the WSGI app exposed by `filter_factory()`. Its core methods are `create_container()`, `get_objs_to_delete()`, `handle_delete_iter()`, `handle_extract_iter()`, `_process_delete()`, and `__call__()`.

## Control Flow
`__call__()` detects `extract-archive` PUTs and `bulk-delete` POST/DELETEs, negotiates response format through `Accept`, and returns an `HTTPOk` whose `app_iter` is a generator. Archive extraction streams a tar file, derives destination paths, creates containers on first use, then sends object PUT subrequests with whitelisted metadata and pax-derived headers. Bulk delete reads newline-delimited URL-encoded names, deletes objects before containers, and runs deletes through `StreamingPile` with bounded concurrency and optional conflict retry.

## State and Persistence
The middleware does not persist local state. It mutates request environ for heartbeat flushing, uses in-memory counters and failure lists per request, and persists only through downstream Swift subrequests that create containers, PUT objects, or DELETE objects/containers. Container auto-creation tracking is per request via `containers_accessed`.

## Dependencies and Integration Points
It depends on Swift `swob`, constraints, `make_subrequest`, `StreamingPile`, heartbeat response formatting, and registry publication for `/info` capabilities. It must sit before middleware that should see internal subrequests as normal Swift requests. It uses `swift.source` values `EA` and `BD` for logging and auth-token forwarding for internal requests.

## Risks and Edge Cases
Outer `200 OK` can hide failures from clients that do not parse the body. Tar streaming must defend against invalid paths, oversized objects, invalid UTF-8, too many created containers, and too many failures. Bulk delete request bodies can be large or malformed, so path-length and operation-count guards are important. Retrying container deletes on conflict can amplify backend load if misconfigured. Archive extraction applies request metadata to every object, which can surprise users if headers are broad.

## Test Signals
Useful tests cover accept negotiation, invalid archive formats, tar/gzip/bzip2 errors, pax metadata mapping, content-length and chunked enforcement, max delete and max extraction limits, object-before-container delete ordering, conflict retry behavior, 5xx to `502 Bad Gateway` aggregation, auth failure short-circuiting, and heartbeat body formats.
