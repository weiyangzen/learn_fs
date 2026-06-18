# sources/object-store/garage/src/api/s3/multipart.rs

## Purpose
Implements multipart upload lifecycle: initiate, upload part, complete, abort, upload lookup, upload-id decoding, complete-body XML parsing, and multipart checksum aggregation.

## Important APIs, Types, And Functions
`handle_create_multipart_upload` creates an uploading object version and an `mpu_table` row. `handle_put_part` streams one part through the PUT block pipeline and records ETag/checksum/size in the MPU. `handle_complete_multipart_upload` validates requested parts, joins part versions into a final object version, calculates multipart ETag and optional checksums, enforces quotas, and finalizes object state. `handle_abort_multipart_upload` marks the uploading object version aborted. Helpers include `get_upload`, `decode_upload_id`, `parse_complete_multipart_upload_body`, `request_checksum_algorithm_and_type`, and `MultipartChecksummer`.

## Control Flow
Initiation generates an upload UUID, chooses a timestamp, extracts metadata, stores encryption metadata and checksum algorithm in an uploading `ObjectVersion`, inserts it into `object_table`, then creates a `MultipartUpload`. Upload-part decodes the upload ID, configures streaming checksums, gets the upload and first block concurrently, validates encryption headers, writes a placeholder part in `mpu_table`, creates a part `Version`, calls `read_and_put_blocks`, verifies stream checksums, and updates the MPU part with final metadata. Completion parses XML, verifies checksum type consistency, requires strictly increasing part numbers, matches requested ETags/checksums against stored completed parts, loads part versions, creates a final `Version` under the upload ID, inserts block refs, calculates final checksum/ETag, checks quotas, optionally rewrites encrypted metadata with final checksum info, and inserts the complete object version.

## State And Persistence
Uses `object_table` for upload markers, aborted markers, and final complete object versions; `mpu_table` for mutable part metadata; `version_table` for uploaded part block lists and final version block lists; `block_ref_table` for final object block references. `InterruptedCleanup` marks a part version deleted if upload-part fails after version creation.

## Dependencies And Integration Points
Depends on `put.rs` for metadata extraction, quotas, chunking, and block writes; `encryption.rs` for SSE-C validation; object/mpu/version/block-ref tables; checksum utilities; and XML response types. COPY part upload also depends on `get_upload` and `decode_upload_id`.

## Risks And Test Signals
Risks include partial failure cleanup, checksum algorithm/type compatibility, final part ordering and block part-number remapping, and quota rollback behavior. The complete path writes final `Version` and block refs before quota check; on quota failure it aborts the object marker but the final version/ref artifacts may remain for cleanup logic. Tests are absent for the full async persistence flow, but XML/checksum helpers have indirect coverage through list and shared checksum logic.
