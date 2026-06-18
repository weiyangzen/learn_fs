# sources/object-store/minio/cmd/api-errors.go

## Purpose
Defines MinIO's S3/Admin API error surface: stable `APIErrorCode` constants, wire-format `APIError`/`APIErrorResponse` structs, the central `errorCodes` HTTP/XML mapping, and translation from internal errors to client-facing S3-compatible failures.

## Important APIs, types, and functions
- `APIError`, `APIErrorResponse`, and `APIErrorCode` are the primary error contract used by response writers and handlers.
- `errorCodeMap.ToAPIErrWithErr`/`ToAPIErr`, `getAPIError`, and `getAPIErrorResponse` produce response-ready values and inject region/request metadata.
- `toAPIErrorCode` classifies context, auth, crypto, KMS, object-layer, bucket-metadata, replication, notification, DNS, and S3 Select errors into stable codes.
- `toAPIError` adds richer descriptions for internal errors, SDK errors, XML syntax, invalid ranges, lifecycle/versioning/replication/tag/policy errors, and cloud backends.

## Control flow
Handlers pass low-level errors through `toAPIErrorCode` or `toAPIError`, then response helpers serialize them. Translation first checks nil, deadline/client-disconnect cases, unwraps nested errors, matches sentinel errors, handles known typed errors, falls back to content-length heuristics, and finally returns `ErrInternalError`. Internal errors get a second interpretation pass in `toAPIError` before being logged if still unclassified.

## State and persistence behavior
This file has no persistence of its own. It reads global site region and request logger context to shape messages and error-response fields. The constant order is persistent API state because `apierrorcode_string.go` and tests depend on it.

## Dependencies and integration points
Integrated with object-layer error types, IAM/auth, crypto/KMS, lifecycle, replication, object lock, tags, policy parsing, DNS, notification/lambda config, hash readers, Azure/GCS/minio-go SDK errors, logger request info, and response serialization in `api-response.go`.

## Risks and edge cases
Adding an error code requires updating `errorCodes` and regenerating the stringer file. Unknown errors expose cause text in `InternalError` descriptions after logging. Context cancellation is intentionally reported as client disconnect only when the request context itself is canceled. Region-specific auth errors rewrite descriptions dynamically.

## Test signals
`api-errors_test.go` verifies representative internal-to-API translations and asserts every non-sentinel `APIErrorCode` has a table entry, non-empty wire code, and HTTP status.
