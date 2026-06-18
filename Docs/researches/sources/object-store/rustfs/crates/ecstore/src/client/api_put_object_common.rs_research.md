# sources/object-store/rustfs/crates/ecstore/src/client/api_put_object_common.rs

## Purpose
Contains shared put-object helpers, especially multipart part-size calculation and upload-id creation.

## Important APIs, Types, and Functions
- `is_object(&ReaderImpl)` and `is_read_at(ReaderImpl)` classify `ReaderImpl::ObjectBody`.
- `optimal_part_info(object_size, configured_part_size)` returns `(total_parts_count, part_size, last_part_size)` while enforcing S3 multipart limits.
- `TransitionClient::new_upload_id` delegates to `initiate_multipart_upload` and returns its `upload_id`.

## Control Flow and State Behavior
`optimal_part_info` treats `object_size == -1` as unknown and substitutes `MAX_MULTIPART_PUT_OBJECT_SIZE`. Configured part sizes are validated against object size, min/max part sizes, and max part count. Without a configured size, it computes the smallest aligned part size that keeps parts within `MAX_PARTS_COUNT`.

## Dependencies and Integration Points
Depends on put options, multipart constants, error constructors, `ReaderImpl`, and `TransitionClient::initiate_multipart_upload`. All multipart upload paths use this function.

## Persistence
No local persistence. `new_upload_id` creates remote multipart-upload state.

## Risks and Edge Cases
Configured part size larger than object size is rejected, although single-part multipart uploads with a part larger than object data can be acceptable if only bytes read are uploaded; this design is stricter. Unknown-size mode sets effective object size to max multipart size, producing max-part loops unless caller has separate EOF handling. `is_read_at` consumes its reader argument and currently duplicates `is_object`.

## Test Signals
No inline tests in this file. Tests should cover boundary sizes, unknown size, configured part size min/max, too many parts, and single small objects.
