# sources/object-store/openstack-swift/swift/common/middleware/formpost.py

## Purpose
`formpost.py` translates signed browser multipart form uploads into one or more pre-authorized Swift object PUT subrequests. It enables HTML form uploads without exposing full auth credentials, using TempURL-style keys and HMAC signatures.

## Important APIs, Types, and Functions
`FormInvalid` and `FormUnauthorized` distinguish bad request from bad signature/auth. `_CappedFileLikeObject` enforces per-file size while streaming. `FormPost.__call__()` detects multipart POSTs. `_translate_form()` parses fields and file parts. `_perform_subrequest()` validates policy/signature and issues a PUT. `_get_keys()` retrieves account and container TempURL keys.

## Control Flow
POST requests with `multipart/form-data` and a boundary are parsed incrementally. Non-file form fields are read up to `MAX_VALUE_LENGTH` and stored lowercased. Each file part increments file count, copies current attributes, applies per-file content headers, and calls `_perform_subrequest()`. The subrequest is pre-authed, chunked, has query string removed, appends filename to `PATH_INFO`, copies delete-at/delete-after and content headers, validates expiry, computes the canonical HMAC body of path, redirect, max file size/count, and expires, and checks the signature against all account/container TempURL keys using allowed digest algorithms. Final response is either plain text or a 303 redirect with status/message parameters.

## State and Persistence
The middleware persists uploaded objects through downstream PUT subrequests. All form attributes, counters, and response state are request-local. It increments digest metric counters through the logger.

## Dependencies and Integration Points
It depends on Swift multipart parsers, TempURL key metadata helpers, digest policy helpers, pre-authed environ creation, account/container info lookups, WSGIContext, and Swift registry. It integrates with auth by making pre-authorized subrequests and typically relies on keystoneauth allowing middleware overrides.

## Risks and Edge Cases
Form field order matters: fields after file parts are not available to those file subrequests. Large fields are truncated at 4096 bytes while the remaining part is drained. Filename is appended directly to the destination path after WSGI conversion. Expired forms, unsupported digest algorithms, invalid signatures, and missing keys deny. File size excess is detected during streaming and converted to a bad request.

## Test Signals
Tests should cover multipart boundary errors, no-file forms, max file count and size enforcement, invalid integer fields, expiry, account/container key retrieval, digest algorithm allow/deprecation info, signature validation with multiple keys, redirect and non-redirect responses, CORS header preservation, per-file content headers, delete-at/delete-after handling, field truncation/draining, and subrequest body/error propagation.
