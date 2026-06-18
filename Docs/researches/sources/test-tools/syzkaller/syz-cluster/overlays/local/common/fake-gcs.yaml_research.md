# sources/test-tools/syzkaller/syz-cluster/overlays/local/common/fake-gcs.yaml

## Purpose
Deploys fake GCS storage for local/test clusters and permits selected ingress.

## Important APIs, types, and functions
Creates `Deployment` `fake-gcs-server` with init container creating `/data/workflow-artifacts` and `/data/blobs`, container `fsouza/fake-gcs-server`, service on port 4443 of type `LoadBalancer`, and network policy `fake-gcs-server-access` allowing ingress from controller, reporter, web-dashboard, workflow pods, and workflow-controller.

## Control flow
Local config sets `STORAGE_EMULATOR_HOST` to the fake GCS service URL and `BLOB_STORAGE_GCS_BUCKET` to `blobs`. Argo workflow artifact config uses `workflow-artifacts`.

## State and persistence behavior
Uses `emptyDir`, so object state is ephemeral for the pod lifetime and lost on restart.

## Dependencies and integration points
Integrates with blob storage code, workflow artifacts, dashboard blob reads, controller uploads, reporter access, and local smoke tests.

## Risks and edge cases
Service type `LoadBalancer` may behave differently in kind/minikube. `emptyDir` means pod restart loses objects. The network policy label `app: reporter` must match actual reporter-server label; researched common policy uses `app: reporter-server`, so label consistency should be checked.

## Test signals
Local smoke exercises blob storage enough for deployments and dashboard availability; Go tests also use app test storage outside Kubernetes.
