<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/training-pv.yaml -->
# sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/training-pv.yaml

Purpose: Static PV/PVC template for TPU training data buckets with active metadata cache and optional file cache.

Important APIs, types, and functions: PV `training-bucket-pv` sets `ReadWriteMany`, `Retain`, dummy storage class, claimRef, active mount options for implicit dirs and metadata cache, and commented file cache/read-ahead options using `<DATASET_SIZE>`. CSI attributes point to `<training-bucket>`, skip access check, and enable metadata prefetch. PVC binds to this PV.

Control flow: CSI applies active mount options during pod mount. File cache is inactive until uncommented by an operator.

State and persistence behavior: Metadata cache can persist indefinitely during the mount. Optional file cache would likely be RAM-backed by the pod and must be sized to the dataset.

Dependencies and integration points: Paired with TPU training pod template. Requires GCS bucket, namespace, and IAM substitution.

Risks and test signals: Stale metadata risk is explicit with `ttl-secs:-1`. Optional cache comments are safer than unlimited defaults, but copying `<DATASET_SIZE>` literally would produce invalid configuration. Tests should include large dataset reads with and without cache.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/samples/gke-csi-yaml/tpu/training-pv.yaml -->
