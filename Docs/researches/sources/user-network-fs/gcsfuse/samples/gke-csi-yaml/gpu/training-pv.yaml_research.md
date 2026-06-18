<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/training-pv.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/training-pv.yaml

Purpose: Static PV/PVC template for GPU training bucket mounts, optimized for metadata caching with optional file cache.

Important APIs, types, and functions: PV `training-bucket-pv` defines `ReadWriteMany`, `Retain`, dummy storage class, claimRef to `training-bucket-pvc`, active mount options for implicit dirs and metadata cache, and commented file-cache/read-ahead options. CSI uses `gcsfuse.csi.storage.gke.io`, `volumeHandle: <training-bucket>`, skips bucket access check, and enables metadata prefetch. Matching PVC binds to the PV.

Control flow: PVC binding is static via `volumeName`; pod mount causes CSI to pass active mount options to gcsfuse.

State and persistence behavior: Metadata cache can persist indefinitely for the mount. File content cache is disabled unless the user uncommentes file-cache options and provides cache backing.

Dependencies and integration points: Works with the GPU training pod template. Requires namespace and bucket placeholder replacement.

Risks and test signals: Active `ttl-secs:-1` can create stale training metadata. Commented cache options include unlimited max size if copied directly, which can exhaust local SSD. GKE integration should test both default metadata-only and cache-enabled modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/training-pv.yaml -->
