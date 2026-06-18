# sources/object-store/rustfs/crates/config/src/constants/body_limits.rs

## Purpose
Defines bounded request/response body sizes for admin APIs and external S3 client responses to reduce memory-exhaustion risk.

## Important APIs, types, and functions
Exports `MAX_ADMIN_REQUEST_BODY_SIZE` (1 MB), `MAX_IAM_IMPORT_SIZE` (10 MB), `MAX_BUCKET_METADATA_IMPORT_SIZE` (100 MB), `MAX_HEAL_REQUEST_SIZE` (1 MB), and `MAX_S3_CLIENT_RESPONSE_SIZE` (10 MB).

## Control flow
No executable flow. HTTP/admin/S3 client code imports these constants when configuring body readers or validators.

## State and persistence behavior
Static numeric constants only.

## Dependencies and integration points
Integrated by admin request handlers, IAM import/export, bucket metadata import, healing APIs, and S3-compatible remote response readers.

## Risks and edge cases
The 100 MB bucket metadata import allowance is intentionally large and should be paired with streaming or careful allocation. Limits are compile-time constants, so deployments cannot tune them without code changes unless higher layers add env overrides. Duplicate rationale comments for S3 response size indicate documentation drift.

## Test signals
No local tests in this file; tests should assert handlers enforce these maximums and reject oversized bodies.
