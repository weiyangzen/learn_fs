# sources/object-store/minio/cmd/api-response_test.go

## Purpose
Unit tests for selected response utility behavior in `api-response.go`.

## Important APIs, types, and functions
- `TestObjectLocation` validates `getObjectLocation`.
- `TestGetURLScheme` validates `getURLScheme`.
- `TestTrackingResponseWriter`, `TestHeadersAlreadyWritten`, and `TestHeadersAlreadyWrittenWrapped` validate response-writer tracking and unwrapping.
- `TestWriteResponseHeadersNotWritten` and `TestWriteResponseHeadersWritten` validate `writeResponse` suppression behavior.

## Control flow
Object-location tests construct requests with host and forwarded scheme variations, including virtual-host bucket domains, then compare exact generated URLs. Writer tests wrap `httptest.ResponseRecorder`, optionally through gzip response wrappers, write headers/bodies, inspect status/body, and confirm later writes are skipped when headers were already marked written.

## State and persistence behavior
No persisted state. Some expected URLs depend on default `globalIsTLS` behavior when no forwarded scheme is present.

## Dependencies and integration points
Uses Go HTTP test utilities and `klauspost/compress/gzhttp` wrappers to represent real middleware wrapping. It guards behavior used by router middleware and response helpers.

## Risks and edge cases
Does not test XML/list response models, metadata filtering, error response body content, invalid status correction, or range headers. The writer tests specifically prevent regressions where a late error response overwrites an already-started response.

## Test signals
Failures show location URL compatibility changes or response-header double-write regressions.
