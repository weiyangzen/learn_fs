# sources/object-store/rustfs/crates/ecstore/src/client/constants.rs

## Purpose
Centralizes transition-client constants for S3 multipart limits, signing payload markers, retry worker count, date formatting, and GetObjectAttributes defaults.

## Important APIs, types, and functions
Exports multipart sizing constants (`ABS_MIN_PART_SIZE`, `MIN_PART_SIZE`, `MAX_PART_SIZE`, `MAX_PARTS_COUNT`, `MAX_SINGLE_PUT_OBJECT_SIZE`, `MAX_MULTIPART_PUT_OBJECT_SIZE`), signing constants (`UNSIGNED_PAYLOAD`, `UNSIGNED_PAYLOAD_TRAILER`, `SIGN_V4_ALGORITHM`, `ISO8601_DATEFORMAT`), `TOTAL_WORKERS`, and GetObjectAttributes constants.

## Control flow
There is no runtime control flow beyond compile-time constant initialization of a `time` format description.

## State and persistence behavior
No state or persistence. Values are shared across request construction, signing, multipart validation, and attribute APIs.

## Dependencies and integration points
The constants are consumed by transition request signing, put/multipart code, and object attributes. It depends on the `time` format-description macro.

## Risks and edge cases
The module imports `lazy_static`, `HashMap`, and `Arc` without using them and has broad allow attributes. Limits should be kept aligned with S3 compatibility rules and any RustFS-specific multipart policy.

## Test signals
No tests are present. Coverage is normally through validation in multipart upload, put-object, and signing tests that assert expected thresholds and header values.
