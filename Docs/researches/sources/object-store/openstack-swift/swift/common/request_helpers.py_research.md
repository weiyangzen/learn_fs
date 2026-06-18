# sources/object-store/openstack-swift/swift/common/request_helpers.py

## Purpose
`request_helpers.py` collects HTTP request and response utilities that need `swob` types without creating circular imports in `swift.common.utils`. It supports parameter validation, internal/reserved namespace validation, metadata header classification, large-object segment streaming, range/multipart translation, backend etag/range control headers, replication-network selection, expired-object access checks, log-info accumulation, and heartbeat response formatting.

## Important APIs, types, and functions
Parameter helpers include `get_param()`, `get_valid_part_num()`, `validate_params()`, `constrain_req_limit()`, and `validate_container_params()`. Path and placement helpers include `get_name_and_placement()` and `split_and_validate_path()`. Metadata helpers include `is_user_meta()`, `is_sys_meta()`, `is_sys_or_user_meta()`, transient sysmeta checks/strippers, prefix constructors, `get_container_update_override_key()`, `get_reserved_name()`, and `split_reserved_name()`. Header utilities include `remove_items()`, `copy_header_subset()`, and `check_path_header()`.

`SegmentedIterable` is the central class for serving static/segmented large objects. It coalesces adjacent segment subrequests, retrieves segment bytes from the WSGI app, validates status, etag, length, MD5, total response length, and max GET time, supports swob range hooks, validates the first segment early, and closes backend iterators. Remaining helpers include `http_response_to_document_iters()`, etag-is-at update/resolve functions, ignore-range update/resolve functions, `is_use_replication_network()`, `get_ip_port()`, `is_open_expired()`, `is_backend_open_expired()`, `append_log_info()`, `get_log_info()`, and `get_heartbeat_response_body()`.

## Control flow and state behavior
Most functions are stateless transformations over requests, headers, metadata, or iterables. Parameter functions decode WSGI strings into native UTF-8 and raise `HTTPBadRequest` or `HTTPPreconditionFailed` for client errors. Internal namespace validation enforces reserved-name placement rules across account/container/object paths.

`SegmentedIterable` maintains iterator state: the original request/app/listing iterator, current backend response, a peeked chunk for first-segment validation, and a validated flag. Its internal pipeline is `_coalesce_requests()` -> `_requests_to_bytes_iter()` -> `_byte_counting_iter()` -> `_time_limited_iter()` -> `_internal_iter()`. It yields bytes lazily, but can be primed by `validate_first_segment()` before response headers are finalized. It closes response iterators on errors, normal completion, and explicit `close()`.

## Dependencies and integration points
This module depends heavily on `swift.common.swob`, `swift.common.utils`, `swift.common.constraints`, `swift.common.storage_policy.POLICIES`, `swift.common.exceptions`, `swift.common.http`, `swift.common.wsgi.make_subrequest`, and `HeaderKeyDict`. It is used by proxy controllers and large-object middleware to validate requests, build backend subrequests, stream SLO/DLO segment bodies, resolve alternate etags from encryption or erasure-coding metadata, and select replication IP/port.

## Risks and edge cases
`SegmentedIterable` must preserve backend iterator closure across many error paths; leaks would hold sockets. Coalesced range construction can be rejected by `Range.ranges_for_length()`, falling back to separate requests. Length and MD5 checks are intentionally skipped or changed for range responses. Once the first segment is validated, later listing/segment errors are logged but may not propagate to the client because bytes may already have been sent. `get_param()` only validates present truthy values, so empty values pass through as defaults. CSV-like etag header handling forbids commas in header names. Heartbeat XML is manually assembled but escapes keys/values.

## Test signals
Important tests include invalid UTF-8 parameters, part-number/range conflicts, container limit constraints, reserved namespace combinations, metadata prefix stripping errors, header subset copy/removal, path-header validation, segment coalescing for raw and object-backed segments, backend 4xx/5xx handling, etag/length/MD5 mismatches, byte-count truncation, max-time failures, first-segment validation behavior, range hooks, multipart response parsing, etag override priority, ignore-range removal, replication-network selection, expired-object flags, and JSON/XML/text heartbeat formatting.
