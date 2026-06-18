# sources/object-store/rustfs/crates/ecstore/src/client/api_s3_datatypes.rs

## Purpose
Defines S3-compatible DTOs used by the transition client for listing buckets/objects/versions, multipart upload operations, copy results, checksum-bearing parts, and multi-delete XML payloads.

## Important APIs, types, and functions
Important structs include `ListBucketV2Result`, `ListBucketResult`, `ListMultipartUploadsResult`, `ObjectPart`, `ListObjectPartsResult`, `InitiateMultipartUploadResult`, `CompleteMultipartUploadResult`, `CompletePart`, `CompleteMultipartUpload`, `DeleteObject`, `DeleteMultiObjects`, and `DeleteMultiObjectsResult`. `ObjectPart::checksum_raw` decodes and validates base64 checksum bytes. `CompleteMultipartUpload::marshal_msg/unmarshal` and `DeleteMultiObjects::marshal_msg/unmarshal` translate Rust DTOs to and from quick-xml wire forms.

## Control flow
Most types are plain data carriers. Multipart completion and multi-delete requests serialize via `quick_xml::se::to_string`; fallback parsing creates internal wire structs with PascalCase field names and converts them into public structs. Checksum helpers select a checksum string by `ChecksumMode`, base64-decode it, and compare decoded length to the algorithm's expected raw byte length.

## State and persistence behavior
The file stores no mutable state. It preserves wire-visible metadata such as ETags, version IDs, part numbers, checksum fields, owner/initiation data, and delete marker metadata so callers can persist or forward it elsewhere.

## Dependencies and integration points
It depends on `s3s::dto::Owner`, serde, quick-xml, `time::OffsetDateTime`, `ChecksumMode`, and `transition_api::ObjectInfo/ObjectMultipartInfo`. It is consumed by list, multipart, checksum, and delete client modules.

## Risks and edge cases
Several result structs have private fields, limiting external construction/inspection. XML naming depends on serde defaults and local wire structs; serialization may not exactly match AWS S3 element names for all fields. Base64 uses RustFS URL-safe-no-pad helpers, which may differ from AWS's normal padded checksum encoding expectations.

## Test signals
No tests live in this file. Behavior is indirectly exercised by `api_remove` multi-delete tests and multipart/listing callers. Direct tests should round-trip XML examples for complete multipart upload and delete objects, including empty version IDs and checksum fields.
