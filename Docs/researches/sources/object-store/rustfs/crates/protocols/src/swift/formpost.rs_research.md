# sources/object-store/rustfs/crates/protocols/src/swift/formpost.rs

## Purpose
`formpost.rs` implements Swift FormPost uploads: browser-based multipart uploads authorized by a TempURL key and HMAC-SHA1 signature instead of exposing Keystone credentials to the browser.

## Important APIs, Types, And Functions
`FormPostRequest` holds redirect URLs, max file size/count, expiration, and signature, with `from_form_fields` and `error_redirect_url`. `generate_signature` signs `path`, redirect, size limit, count limit, and expiry. `validate_formpost` checks expiration and signature. `UploadedFile` stores parsed file fields. `build_redirect_url`, `parse_boundary`, `parse_multipart_form`, `extract_field_name`, `extract_filename`, and `handle_formpost` implement parsing, validation, object uploads, and `303 See Other` responses.

## Control Flow
`handler.rs` detects container POST requests with `multipart/form-data`, fetches the account TempURL key, collects the full request body, and calls `handle_formpost`. The handler parses fields/files, validates the signed request, enforces count and per-file size, uploads each file via `object::put_object`, accumulates upload errors, and redirects to success or error URL with status/message query parameters.

## State, Persistence, And Dependencies
No local state is persisted. Uploaded objects are stored through `object.rs`; authorization depends on TempURL key metadata from the account module. Dependencies include HMAC-SHA1, hex, URL encoding, HTTP response types, and credentials.

## Integration Points
The path signed by the form is constructed in `handler.rs` as `/v1/{account}/{container}`. Object names are derived directly from client filenames and passed to `object::put_object`, so object validation and container mapping remain centralized in object storage code.

## Risks And Test Signals
The multipart parser converts the entire body to UTF-8-lossy text, splits on boundary strings, joins lines with `\n`, trims trailing content, and stores each file fully in memory; binary files, CRLF preservation, embedded boundary bytes, and large uploads are risky. Signature comparison is a normal string comparison rather than constant-time verification. Redirect URL construction always appends `?status=...`, ignoring existing query strings. Tests cover signature sensitivity, expiration validation, redirect construction, and field parsing, but not multipart binary correctness or end-to-end upload.
