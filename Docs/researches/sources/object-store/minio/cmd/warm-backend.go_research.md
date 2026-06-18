# sources/object-store/minio/cmd/warm-backend.go

Defines the remote tier backend abstraction. `WarmBackend` requires put, put-with-metadata, get, remove, and in-use operations; `WarmBackendGetOpts` describes byte ranges; `remoteVersionID` hides provider-specific version IDs.

`checkWarmBackend` actively probes configured credentials by putting, getting, draining, and deleting a fixed `probeobject`. It preserves backend-down errors and maps common bucket/credential failures; other failures become operation-specific `tierPermErr`. `newWarmBackend` dispatches S3, Azure, GCS, or MinIO constructors from `madmin.TierConfig`, logs constructor errors, optionally probes, and returns unsupported type/config errors.

The probe has real remote side effects and can leave `probeobject` behind if cleanup fails. Risks include object-name collision, partial cleanup, provider-specific version behavior, and broad constructor-error collapse. No direct tests in this subset cover it.
