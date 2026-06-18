# sources/object-store/garage/src/api/s3/list.rs

## Purpose
Implements S3 listing APIs for objects, multipart uploads, and multipart upload parts. It handles V1/V2 object pagination, delimiter/common-prefix semantics, upload markers, URL encoding, and checksum visibility for encrypted multipart parts.

## Important APIs, Types, And Functions
Query structs are `ListQueryCommon`, `ListObjectsQuery`, `ListMultipartUploadsQuery`, and `ListPartsQuery`. Entry points are `handle_list`, `handle_list_multipart_upload`, and `handle_list_parts`. `fetch_list_entries` is the generic pagination loop over object-table ranges. `ObjectAccumulator` and `UploadAccumulator` implement `ExtractAccumulator`. `fetch_part_info` filters completed MPU parts and computes pagination. `RangeBegin` represents inclusive/exclusive cursor modes and upload-id cursor modes.

## Control Flow
Object and upload listing create a table range IO closure with different `ObjectFilter` values, build an accumulator, compute the starting cursor from query markers/tokens, and repeatedly call `get_range` with `page_size + 1`. The accumulator either extracts object entries, common prefixes, or uploads until full. Pagination returns the next marker/token depending on list version and whether the next cursor is inclusive or exclusive.

List parts decodes upload ID, loads the upload through `multipart::get_upload`, checks whether request headers can decrypt the upload metadata, filters completed parts, and emits checksum fields only when encryption is absent or decryption headers are valid.

## State And Persistence
Read-only. Reads `object_table` ranges and `mpu_table` state through `get_upload`. It relies on object version states to distinguish data objects from multipart upload markers and on MPU part CRDT ordering to select the latest completed part per part number.

## Dependencies And Integration Points
Depends on Garage object and MPU tables, `EnumerationOrder::Forward`, S3 XML list result types, URI encoding helpers, multipart upload decoding, encryption metadata validation, and checksum value representations.

## Risks And Test Signals
Listing compatibility is delicate. Risks include off-by-one pagination, inclusive token encoding, delimiter skipping via `key_after_prefix`, and lexicographic upload-id ordering. The code has substantial unit tests for common prefixes, upload extraction, pagination over synthetic ranges, and list-part pagination/filtering. It does not directly test object V2 continuation token round trips or encrypted checksum hiding.
