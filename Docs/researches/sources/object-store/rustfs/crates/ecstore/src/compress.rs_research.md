# sources/object-store/rustfs/crates/ecstore/src/compress.rs

## Purpose
Decides whether an object should be disk-compressed based on process environment, object name, content type, content encoding, include filters, and hard-coded exclusion lists.

## Important APIs, types, and functions
Exports environment variable names, default extension/MIME include lists, strict excluded extensions/content types, `MIN_DISK_COMPRESSIBLE_SIZE`, `parse_added_exclude_extensions`, and `is_disk_compressible`. Internal helpers parse booleans/CSV values, normalize extensions, detect configured patterns, detect existing content encodings, and cache `DiskCompressionConfig` in a `OnceLock`.

## Control flow
On first use, environment variables are parsed once. `is_disk_compressible` returns false if compression is disabled, if content encoding is already meaningful other than `identity` or `aws-chunked`, if extension/content type is excluded, or if an added exclusion matches. If include filters are empty it compresses everything except exclusions; otherwise it requires either extension or MIME include match.

## State and persistence behavior
The process-global compression config is immutable after first use because of `OnceLock`. There is no disk persistence. The decision controls later object storage behavior but this module only computes eligibility.

## Dependencies and integration points
It uses RustFS string matching helpers and HTTP headers. It is expected to be consulted by PUT/storage code before deciding on at-rest compression.

## Risks and edge cases
Environment changes after first call are ignored. MIME matching depends on simple pattern utilities. Default includes contain `.tar` and `.bin`, while exclusions include tar MIME types but not `.tar` extension, so behavior depends on content type accuracy. Invalid `Content-Encoding` is treated as already encoded and therefore not compressible.

## Test signals
Unit tests cover enabled parsing, include parsing/defaults, broad excluded extensions and content types, positive text/json/html cases, content-encoding skip logic, added exclusion parsing/application, and empty include filters compressing all non-excluded objects.
