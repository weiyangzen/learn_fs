<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/checkpointing-pv.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/checkpointing-pv.yaml

Purpose: Static PV/PVC template for TPU checkpointing buckets using the GKE gcsfuse CSI driver.

Important APIs, types, and functions: PV `checkpoint-bucket-pv` uses `ReadWriteMany`, `Retain`, dummy storage class, claimRef, mount options for implicit dirs, metadata cache, unlimited file cache, range-read whole-file caching, parallel downloads, read-ahead, and streaming writes. CSI attributes include driver `gcsfuse.csi.storage.gke.io`, `volumeHandle: <checkpoint-bucket>`, `skipCSIBucketAccessCheck`, and metadata prefetch. PVC `checkpoint-bucket-pvc` binds to the PV.

Control flow: Static PVC binding and CSI mount pass all mount options to gcsfuse when a TPU checkpoint pod consumes the PVC.

State and persistence behavior: Checkpoints persist in GCS; local file cache is usually RAM-backed by the TPU pod template. Metadata prefetch populates cache at mount time.

Dependencies and integration points: Designed to pair with TPU checkpointing pod YAML and TPU RAM disk cache. Requires bucket/namespace substitution.

Risks and test signals: Unlimited file cache on RAM disk can exhaust memory. `skipCSIBucketAccessCheck` can defer bucket misconfiguration errors. Streaming writes should be tested under checkpoint save/restore workloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/checkpointing-pv.yaml -->
