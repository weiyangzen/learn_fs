# sources/test-tools/syzkaller/pkg/asset/storage.go

## Purpose
Core asset upload, compression, dashboard reporting, and garbage-collection logic for syzkaller build/crash artifacts.

## Important APIs, Types, and Functions
`Storage` combines config, backend, dashboard API, and tracer. Public methods include `StorageFromConfig`, `AssetTypeEnabled`, `UploadBuildAsset`, `ReportBuildAssets`, `UploadCrashAsset`, and `DeprecateAssets`. Supporting types include `Dashboard`, `ExtraUploadArg`, `DeprecateStats`, `StorageBackend`, `Compressor`, `FileExistsError`, and `wrappedWriteCloser`.

## Control Flow
Uploads validate name/type/enabled status, create a unique or tagged path, pick xz or custom gzip compressor, request a backend writer, stream bytes, close wrappers, and return a download URL. Build uploads add commit prefixes to names. Reporting sends assets to dashboard. Deprecation queries needed URLs, converts them to backend paths, lists existing objects, protects recent uploads, refuses deletion on suspicious zero intersection, and removes stale paths while tolerating concurrent missing-object races.

## State and Persistence Behavior
Persists compressed artifacts in the backend and dashboard asset references via `AddBuildAssets`. Local state is in-memory. Deprecation mutates backend storage by deleting objects older than the embargo and not needed by dashboard.

## Dependencies and Integration Points
Depends on dashboard API types, GCS object metadata, debug tracing, xz/gzip compressors, build metadata, and backend implementations.

## Risks and Test Signals
Risks include upload/write-close error ordering, duplicate-tag races, incorrect content encoding, accidental deletion from malformed dashboard URLs, and time-based embargo mistakes. Tests cover upload naming/compression, HTML gzip extension preservation, disabled types, duplicate content skip, deprecation protection, multi-bucket handling, and invalid URL aborts.
