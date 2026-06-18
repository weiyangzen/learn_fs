# sources/object-store/rustfs/crates/ecstore/src/client/api_get_options.rs

## Purpose
Defines GET/HEAD option structures for object operations and helpers for conditional headers, ranges, checksum mode, versioning, part-number selection, and query parameters.

## Important APIs, Types, and Functions
- `AdvancedGetOptions` carries internal replication flags.
- `GetObjectOptions` stores arbitrary headers, request parameters, version ID, part number, checksum mode, and internal options.
- `StatObjectOptions` aliases `GetObjectOptions`.
- `header` validates stored headers into `HeaderMap` and adds `x-amz-checksum-mode: ENABLED` when requested.
- `set` validates a header name/value before storing it.
- `set_req_param`/`add_req_param`, `set_match_etag`, `set_match_etag_except`, `set_unmodified`, `set_modified`, `set_range`, and `to_query_values` build request metadata.

## Control Flow and State Behavior
The struct is mutable caller-owned state. Header setters validate via `http` types and store canonical header-name strings. `header()` is tolerant of invalid prepopulated values: it logs and skips them. `to_query_values` combines version ID, part number, and arbitrary request params.

## Dependencies and Integration Points
Uses `http::{HeaderMap, HeaderName, HeaderValue}`, `time::OffsetDateTime`, tracing warnings, and `err_invalid_argument`. All GET/stat/list-adjacent client methods consume this option type.

## Persistence
No persistence. It shapes outgoing request metadata.

## Risks and Edge Cases
Date headers use `OffsetDateTime::to_string()` rather than an HTTP-date/RFC7231 formatter, which may not match S3 expectations. Suffix range behavior for `set_range(0, negative)` emits `bytes=-N` only when `end < 0`; the sign convention should be documented. Invalid headers inserted directly into `headers` are skipped only at `header()` time.

## Test Signals
Inline tests cover normal range header creation, rejection of invalid header values in `set`, and skipping invalid prepopulated header values.
