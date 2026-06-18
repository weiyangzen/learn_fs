# sources/test-tools/syzkaller/pkg/asset/backend_gcs.go

## Purpose
Google Cloud Storage implementation of the asset `StorageBackend` interface.

## Important APIs, Types, and Functions
`cloudStorageBackend` holds `gcs.Client`, bucket, and tracer. `makeCloudStorageBackend` constructs the client. `writeErrorLogger` logs write/close errors. Backend methods implement upload, download URL generation, URL-to-path parsing, list, and remove.

## Control Flow
Upload checks for existing object, obtains a writer with content metadata, wraps it for logging, and returns the save path. `downloadURL` delegates to GCS helpers. `getPath` parses URLs, accepts only storage Google domains, checks bucket prefix, and strips it. `remove` maps GCS not-found to `ErrAssetDoesNotExist`.

## State and Persistence Behavior
Persists objects in GCS. Local state is just client configuration and tracing.

## Dependencies and Integration Points
Depends on `pkg/gcs`, `debugtracer`, URL parsing, and `Storage` upload/deprecation paths.

## Risks and Test Signals
Risks include best-effort exists check races, allowed-domain regex precedence, bucket mismatch, and delayed writer errors. Tests cover URL generation/parsing and bucket/domain rejection.
