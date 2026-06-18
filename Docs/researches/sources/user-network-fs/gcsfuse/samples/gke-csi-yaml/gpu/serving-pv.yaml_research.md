<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/serving-pv.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/serving-pv.yaml

Purpose: Static PV/PVC template for GPU serving bucket mounts using gcsfuse CSI with aggressive read cache options.

Important APIs, types, and functions: PV `serving-bucket-pv` uses `ReadWriteMany`, retained reclaim policy, dummy storage class, and `mountOptions` for implicit dirs, disabled negative metadata cache, indefinite metadata TTL, unlimited stat/file cache, range-read whole-file caching, parallel downloads, and `read_ahead_kb=1024`. CSI uses `volumeHandle: <serving-bucket>`, skips bucket access check, and enables metadata prefetch on mount. PVC `serving-bucket-pvc` binds to that PV.

Control flow: Kubernetes binds PVC to PV; the CSI driver uses the mount options when a pod consumes the PVC.

State and persistence behavior: GCS stores model artifacts; local cache state is external to this YAML and driven by pod/cache configuration. Metadata is prefetched and cached indefinitely by gcsfuse.

Dependencies and integration points: Must be consumed by serving pod template and parameterized with real bucket and namespace values.

Risks and test signals: Indefinite metadata and unlimited file cache favor performance over freshness/resource bounds. `skipCSIBucketAccessCheck` can hide configuration errors until pod I/O. Serving validation should measure cold and warm model reads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/serving-pv.yaml -->
