# sources/user-network-fs/rclone/backend/oracleobjectstorage/copy.go

Purpose: implements server-side copy for Oracle Object Storage and waits for the asynchronous OCI work request to finish.

Important APIs: `(*Fs).Copy` validates the source is an Oracle `*Object`, creates a destination `Object`, calls `f.copy`, then returns `f.NewObject` for the copied remote. `copy` builds `CopyObjectDetails` with source/destination names, region, namespace, bucket, object metadata, and BYOK headers. `copyObjectWaitForWorkRequest` polls work request state using `StateChangeConf`. `getObjectStorageErrorFromWorkRequest` collects work request error messages.

Control flow: before copy, if destination bucket differs from source, the backend checks and creates it if necessary. The copy request is submitted through `ObjectStorageClient.CopyObject`; OCI returns `OpcWorkRequestId`. The waiter treats accepted/in-progress/canceling as pending and completed/canceled/failed as terminal. Failed work requests are expanded by listing work request errors. The returned destination object is fetched after copy so metadata and size reflect server state.

State and persistence behavior: creates or overwrites remote destination objects and may create destination buckets. Metadata is copied from `srcObj.meta` using `metadataWithOpcPrefix`; callers should ensure source metadata has been loaded when metadata fidelity matters. Local state is limited to temporary request structs.

Dependencies and integration points: depends on OCI SDK `objectstorage` and `common`, BYOK helper `useBYOKCopyObject`, main backend bucket helpers, pacer/retry logic, and `StateChangeConf` from `waiter.go`.

Risks: server-side copy requires OCI IAM policy granting objectstorage service permissions; otherwise users must fall back to download/upload. Work request polling uses `context.Background()` inside the refresh function rather than the caller context for each `GetWorkRequest`, reducing cancellation precision. Canceled work requests are listed as target states but only failed state triggers an explicit error check, so canceled behavior depends on waiter result semantics. Metadata copying can miss metadata if the source object's `meta` map is nil.

Test signals: Oracle integration tests may exercise copy through fstests and copy cutoff controls, but no direct work-request failure or IAM-policy test is in this subset.
