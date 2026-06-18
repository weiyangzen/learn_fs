<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/checkpointing-pod.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/checkpointing-pod.yaml

Purpose: Kubernetes Pod template for GPU checkpointing workloads using the GKE gcsfuse CSI driver with a checkpoint bucket PVC.

Important APIs, types, and functions: Defines a `v1/Pod` with `gke-gcsfuse/volumes: "true"` annotation, placeholder namespace, workload container placeholder, `checkpoint-bucket-vol` mounted at `/checkpoint-data`, service account placeholder, and PVC-backed volume `checkpoint-bucket-pvc`. Optional metadata-prefetch resource annotations and RAM disk cache `emptyDir` are commented.

Control flow: Kubernetes schedules the pod; the GKE gcsfuse CSI integration sees the annotation, injects/uses the CSI volume, and mounts the checkpoint PVC into the workload container.

State and persistence behavior: Checkpoint data is persisted in the GCS bucket behind the PVC. Optional in-memory cache volume would be ephemeral and pod-scoped if uncommented.

Dependencies and integration points: Requires GKE gcsfuse CSI support, Workload Identity/service account wiring via `<YOUR_K8S_SA>`, and a matching `checkpoint-bucket-pvc` from the PV template.

Risks and test signals: The workload container is an ellipsis placeholder and is not valid as-is. Missing service account permissions or absent PVC prevents mounting. Optional metadata prefetch annotations require minimum GKE version `1.32.3-gke.1717000`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/gpu/checkpointing-pod.yaml -->
