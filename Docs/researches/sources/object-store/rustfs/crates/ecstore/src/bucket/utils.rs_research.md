# sources/object-store/rustfs/crates/ecstore/src/bucket/utils.rs

## Purpose
This file centralizes bucket/object name validation, XML serialization helpers, and argument validation for object, list, and multipart APIs. It translates invalid input into crate `Error` or `StorageError` variants before storage-layer operations touch the filesystem.

## Important APIs, Types, and Functions
- `is_meta_bucketname` identifies internal metadata buckets using `RUSTFS_META_BUCKET` and `MIGRATING_META_BUCKET`.
- `check_bucket_name_common`, `check_valid_bucket_name`, and `check_valid_bucket_name_strict` enforce length, reserved name, IP-address rejection, dot/dash adjacency, and regex rules.
- `check_valid_object_name_prefix` and `check_valid_object_name` provide simple ASCII/length/non-empty checks.
- `deserialize`, `serialize_content`, and `serialize` wrap `s3s::xml` deserialization/serialization.
- `has_bad_path_component`, `is_valid_object_prefix`, and `is_valid_object_name` reject `.`/`..` path segments, double slashes, NULs, invalid UTF-8, and oversized paths.
- Argument validators include `check_copy_obj_args`, `check_get_obj_args`, `check_del_obj_args`, `check_bucket_and_object_names`, `check_list_objs_args`, `check_list_multipart_args`, `check_object_args`, `check_new_multipart_args`, `check_multipart_object_args`, `check_put_object_part_args`, `check_list_parts_args`, `check_complete_multipart_args`, `check_abort_multipart_args`, and `check_put_object_args`.

## Control Flow and State Behavior
Bucket validation first trims and checks basic constraints, then applies strict or relaxed regexes. Object prefix validation scans path bytes manually for bad path components, treating `/` and `\` as separators, trimming whitespace inside each segment. Higher-level API validators compose bucket validation, length/slash checks, prefix/object checks, and upload-id base64 decoding.

## Dependencies and Integration Points
The file depends on disk metadata bucket constants, crate error types, `regex`, `rustfs_utils::path::SLASH_SEPARATOR`, `s3s::xml`, `base64_simd`, and tracing instrumentation. It is a common precondition layer for bucket, object, and multipart handlers.

## Persistence
No persistence. It prevents invalid names from reaching persistence layers where path traversal, filesystem incompatibility, or ambiguous object paths could occur.

## Risks and Edge Cases
- `check_valid_object_name_prefix` rejects non-ASCII despite its error message saying non-UTF-8; `is_valid_object_prefix` accepts broader valid UTF-8. Callers using different validators may get inconsistent behavior.
- Empty upload IDs decode successfully with `URL_SAFE_NO_PAD`; the tests currently document that `check_multipart_object_args` accepts an empty upload ID after decode, which may conflict with S3 expectations.
- Relaxed bucket regex allows uppercase, underscore, and colon; strict validation is used in most external object validators.
- `serialize_content` unwraps UTF-8 conversion, assuming XML serializer output is valid UTF-8.
- Prefix validation rejects double slashes and dot path components even though some S3-compatible clients may expect arbitrary byte-like keys.

## Test Signals
Inline tests cover object names, prefixes, bucket/object argument validation, list validation, multipart upload-id validation, and put-object validation. They explicitly cover path traversal, double slash, NUL, long paths, and the current empty-upload-id behavior.
