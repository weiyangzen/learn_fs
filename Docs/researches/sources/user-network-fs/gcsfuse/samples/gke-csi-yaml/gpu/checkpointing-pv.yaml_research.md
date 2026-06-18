<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/checkpointing-pv.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/checkpointing-pv.yaml

Purpose: Kubernetes PersistentVolume and PersistentVolumeClaim template for GPU checkpointing buckets mounted through the GKE gcsfuse CSI driver.

Important APIs, types, and functions: Defines a `PersistentVolume` named `checkpoint-bucket-pv` with `ReadWriteMany`, `Retain`, dummy `gcsfuse-sc`, claimRef to `checkpoint-bucket-pvc`, gcsfuse mount options for implicit dirs, metadata cache, unlimited file cache, whole-file range caching, parallel downloads, kernel read-ahead, and streaming writes. CSI attributes set driver `gcsfuse.csi.storage.gke.io`, `volumeHandle: <checkpoint-bucket>`, `skipCSIBucketAccessCheck`, and `gcsfuseMetadataPrefetchOnMount`. The second YAML document defines the matching PVC.

Control flow: The statically bound PVC claims the named PV. During pod mount, CSI passes mountOptions and volumeAttributes to gcsfuse.

State and persistence behavior: The PV is retained after PVC deletion. Cached content is node/pod side, while checkpoint objects persist in GCS. Metadata prefetch populates metadata cache at mount time.

Dependencies and integration points: Must be paired with a pod mounting `checkpoint-bucket-pvc`. It depends on a real GCS bucket name replacing `<checkpoint-bucket>` and correct namespace substitution.

Risks and test signals: Unlimited cache and read-ahead can pressure local disk. `skipCSIBucketAccessCheck: "true"` defers access failure to runtime operations. Streaming writes are checkpoint-specific and should be validated with write-heavy tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/checkpointing-pv.yaml -->
