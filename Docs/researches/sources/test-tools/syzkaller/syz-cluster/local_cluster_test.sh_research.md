# sources/test-tools/syzkaller/syz-cluster/local_cluster_test.sh

## Purpose
End-to-end smoke script for building syz-cluster containers, deploying a local test cluster with kind, and verifying dashboard reachability.

## Important APIs, types, and functions
Shell script with `set -e`, dependency checks for `kind` and `kubectl`, cluster name `syz-cluster-test`, local kubeconfig path `.test-kubeconfig`, and `cleanup` trap. It runs `make all-containers`, `kind load docker-image`, `make k8s-config-local-infra`, `make migrate-local`, and `make k8s-config-test | kubectl apply -f -`.

## Control flow
The script deletes any existing test cluster, creates a new kind cluster, builds and loads local images, deploys infrastructure, runs database migrations, deploys syz-cluster test config, waits for core deployments, port-forwards the dashboard service, curls `/`, and requires HTTP 200. On failure it dumps pod status/logs/describes and leaves the cluster intact. On success it deletes the cluster and kubeconfig.

## State and persistence behavior
Creates a temporary local Kubernetes cluster and Docker images tagged `local_smoke/`. Kubeconfig is written under the source directory. Failure intentionally preserves cluster state for debugging.

## Dependencies and integration points
Depends on Docker, kind, kubectl, Makefile targets, local overlays, database migration job, and dashboard service. It exercises dashboard, controller, reporter server, series tracker, local Spanner emulator, fake GCS, and Argo-related config enough to reach availability.

## Risks and edge cases
The script uses `grep` and unquoted `$IMAGES`; no images found or image names with unexpected whitespace would fail. Port-forward uses fixed local port 8080 and a fixed sleep. Cleanup kills the port-forward only on the explicit HTTP failure path and after success; abrupt intermediate failures rely on process cleanup by shell exit/environment.

## Test signals
Provides high-value cluster integration signal that manifests render, images start, migrations run, deployments become available, and the dashboard responds with HTTP 200.
