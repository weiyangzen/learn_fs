# sources/object-store/garage/src/api/s3/get.rs

## Purpose
Implements S3 GET and HEAD object reads, including metadata headers, conditional requests, range reads, partNumber reads, checksum response headers, SSE-C decryption, and streamed block responses.

## Important APIs, Types, And Functions
`handle_head` and `handle_get` are context-aware entry points; `handle_head_without_ctx` and `handle_get_without_ctx` are also used by website serving. `object_headers` builds S3 response headers from object version metadata and decrypted metadata. `GetObjectOverrides` represents response header overrides. `full_object_byte_stream` streams inline or block-backed data. `handle_get_range`, `handle_get_part`, `body_from_blocks_range`, and `calculate_part_bounds` implement partial reads. `PreconditionHeaders` parses and evaluates HTTP and copy-source preconditions.

## Control Flow
GET/HEAD fetch the object from `object_table`, choose the latest complete/data version, reject delete markers, extract `ObjectVersionMeta`, and call `EncryptionParams::check_decrypt` to validate SSE-C headers and get plaintext metadata. Conditional headers are evaluated before content handling. GET rejects simultaneous `partNumber` and `Range`. Full GET streams the whole object and applies response overrides. Range and part reads return 206 and intentionally skip override headers.

For block-backed full reads, the first block is fetched immediately while a task loads the version table and streams remaining blocks in order. Range reads load the version table, select intersecting blocks by true object offset, then slices chunks from decrypted block streams as they pass through.

## State And Persistence
This module is read-only. It reads `object_table`, `version_table`, and block data through `block_manager` via `EncryptionParams::get_block`. It treats `Version.deleted` as a transient internal consistency error rather than a missing key.

## Dependencies And Integration Points
Integrates with `copy.rs` by exporting `full_object_byte_stream`, `PreconditionHeaders`, and `check_version_not_deleted`. It depends on encryption, checksum helpers, Hyper headers, `http_range`, Garage object/version tables, and ordered block RPC tags.

## Risks And Test Signals
Important risks include partial stream error handling: a comment notes that sending an error stream item after bytes may still look successful in some client cases. Range handling assumes `all_blocks` is non-empty for block objects. Conditional request logic truncates timestamps to seconds to match HTTP date precision. There are no local tests in this file; precondition, range, and SSE-C behavior require integration coverage.
