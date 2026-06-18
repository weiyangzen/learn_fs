# sources/object-store/rustfs/crates/ecstore/src/client/object_api_utils.rs

## Purpose
Contains object API helper utilities for PUT readers, GET range reader construction, compressed-offset scaffolding, and ETag normalization.

## Important APIs, types, and functions
`PutObjReader` wraps `rustfs_rio::HashReader` and can expose the current MD5 checksum or replace the reader after encryption. `ObjReaderFn` is a closure type for creating `GetObjectReader`. `new_getobjectreader` maps requested ranges or part numbers to object-reader closures plus offset/length. `to_s3s_etag` and `get_raw_etag` normalize metadata ETags.

## Control flow
Part-number requests are converted to byte ranges by walking object parts and summing `actual_size`. Explicit range requests are validated through `HTTPRangeSpec::get_offset_length`; success returns a closure wrapping the input buffer into `GetObjectReader`. ETag conversion classifies weak `W/"..."`, quoted strong, and plain values.

## State and persistence behavior
No persistent state. Functions consume object metadata and return transient readers/ranges. ETag helpers interpret metadata maps without mutation.

## Dependencies and integration points
The module integrates store API types (`ObjectInfo`, `ObjectOptions`, `HTTPRangeSpec`, `GetObjectReader`), S3 DTO `ETag`, file metadata part info, and RustFS hash readers. It is used by object GET/PUT paths.

## Risks and edge cases
`new_getobjectreader` returns `InvalidRange` when no range/part number is supplied, so callers must handle full-object reads elsewhere. Compression and encryption paths are mostly placeholders. `part_number_to_rangespec` uses `i < part_number`, which treats part numbers as one-based but may include one extra part depending on caller expectations.

## Test signals
Local tests cover strong, weak, quoted, malformed, and empty ETag conversion, plus raw ETag extraction with `etag`, fallback `md5Sum`, and missing metadata.
