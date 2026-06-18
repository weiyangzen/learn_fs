<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/serving-pod.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/serving-pod.yaml

Purpose: Kubernetes Pod template for TPU serving workloads that mount serving data from GCS and use memory-backed gcsfuse cache.

Important APIs, types, and functions: Defines a `v1/Pod` with gcsfuse CSI annotation, placeholder namespace/container, `serving-bucket-vol` mounted at `/serving-data`, service account placeholder, active `gke-gcsfuse-cache` `emptyDir.medium: Memory`, and PVC `serving-bucket-pvc`.

Control flow: GKE injects/activates gcsfuse volume handling based on pod annotation and mounts the PVC before workload start.

State and persistence behavior: Model data persists in GCS; cache contents live in pod memory and are lost at pod termination.

Dependencies and integration points: Requires TPU serving workload spec, matching serving PV/PVC, bucket IAM, and sufficient memory allocation.

Risks and test signals: The RAM disk cache is active by default and can compete with serving memory. Placeholder container syntax must be replaced. Tests should verify cache-backed model reads and pod resource sizing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/serving-pod.yaml -->
