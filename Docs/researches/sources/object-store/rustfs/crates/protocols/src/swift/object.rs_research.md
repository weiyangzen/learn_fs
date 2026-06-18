# sources/object-store/rustfs/crates/protocols/src/swift/object.rs

## Purpose
`object.rs` implements Swift object CRUD and server-side copy on top of the RustFS S3/object-store layer. It handles Swift object-name validation, tenant-aware bucket mapping, metadata extraction, expiration metadata, symlink metadata, streaming PUT/GET, HEAD, DELETE, POST metadata replacement, COPY, and Range parsing.

## Important APIs, Types, And Functions
`ObjectKeyMapper` validates and maps Swift object names to S3 keys, decodes/encodes URL names, detects directory markers, and normalizes paths. `put_object` streams uploads from `AsyncRead` through `HashReader` and `PutObjReader`. `put_object_with_metadata` is used for DLO/SLO marker or manifest writes. `get_object`, `head_object`, `delete_object`, `update_object_metadata`, and `copy_object` wrap RustFS storage operations. Header parsers include `parse_destination_header`, `parse_copy_from_header`, `parse_range_header`, and `format_content_range`. Private helpers validate metadata and sanitize storage errors.

## Control Flow
Most operations validate account access, validate object name, map container to tenant-prefixed bucket through `ContainerMapper`, resolve the object store handle, build `ObjectOptions`, and call bucket/object APIs. Upload extracts `x-object-meta-*`, content type, expiration headers, and symlink target before metadata validation and storage upload. Copy verifies source and destination, chooses source or replacement metadata, then calls storage-layer `copy_object`.

## State, Persistence, And Dependencies
Object bytes and metadata persist in the RustFS object store. Metadata includes user-defined Swift headers, content type, `x-delete-at`, and symlink targets. Dependencies include account access validation, container mapping, symlink and expiration helpers, RustFS object-store traits, `HashReader`, `BucketOptions`, Axum headers, and tracing.

## Integration Points
`handler.rs`, `dlo.rs`, `formpost.rs`, SLO/versioning modules, and symlink resolution all call this module. DLO registration uses `put_object_with_metadata`; regular object operations use streaming APIs from the handler. Quota is checked in `handler.rs` before calling `put_object` when content length is available.

## Risks And Test Signals
Storage error classification relies on matching error strings such as "does not exist" or "not found". Metadata header extraction lowercases the whole header name and strips `x-object-meta-`, so stored key names are normalized but remove-header semantics are absent. Unknown content length uses `-1`, which may weaken quota and size enforcement. Encryption is not integrated. Range parsing here differs from handler-local range calculation and DLO range parsing. Tests cover object-name validation, URL encoding, path normalization, destination/copy header parsing, range parsing, and content-range formatting, but not live storage behavior.
