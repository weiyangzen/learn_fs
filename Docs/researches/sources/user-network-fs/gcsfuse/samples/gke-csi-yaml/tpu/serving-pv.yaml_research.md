<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/serving-pv.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/serving-pv.yaml

Purpose: Static PV/PVC template for TPU serving buckets with gcsfuse CSI read-cache optimizations.

Important APIs, types, and functions: PV `serving-bucket-pv` includes implicit dirs, disabled negative metadata cache, indefinite metadata cache, unlimited stat/file caches, whole-file range-read caching, parallel downloads, and `read_ahead_kb=1024`. CSI points to `<serving-bucket>` and enables skipped bucket access check plus metadata prefetch. PVC `serving-bucket-pvc` binds to that PV.

Control flow: Kubernetes binds PVC to PV; CSI transforms mount options into gcsfuse command/config behavior for the consuming pod.

State and persistence behavior: GCS is persistent storage; local cache is pod/node-side and, in the paired TPU pod, RAM-backed.

Dependencies and integration points: Consumed by TPU serving pod template and requires bucket/namespace substitution.

Risks and test signals: Unlimited RAM-backed cache can overrun memory, and indefinite metadata can stale model artifact views. `skipCSIBucketAccessCheck` should be used only when IAM/bucket existence is validated elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/serving-pv.yaml -->
