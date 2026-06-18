<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/training-pod.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/training-pod.yaml

Purpose: Kubernetes Pod template for TPU training workloads mounting GCS training data through gcsfuse CSI.

Important APIs, types, and functions: Defines a gcsfuse-enabled `v1/Pod`, placeholder workload container, `training-bucket-vol` mounted at `/training-data`, service account placeholder, and PVC `training-bucket-pvc`. In-memory cache volume is commented and should be enabled only if the dataset fits.

Control flow: GKE CSI mounts the training PVC into the pod when the annotation is present.

State and persistence behavior: Training data remains in GCS. No active cache volume is created by default, limiting memory pressure for large datasets.

Dependencies and integration points: Requires matching TPU training PV/PVC and bucket IAM. Placeholder fields must be replaced for a valid pod.

Risks and test signals: Enabling RAM cache without dataset sizing can exhaust memory. Default metadata-only cache should be tested for data-loading performance and freshness assumptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/training-pod.yaml -->
