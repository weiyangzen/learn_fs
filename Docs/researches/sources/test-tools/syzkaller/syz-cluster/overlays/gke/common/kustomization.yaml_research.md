# sources/test-tools/syzkaller/syz-cluster/overlays/gke/common/kustomization.yaml

## Purpose
Common GKE overlay for syz-cluster.

## Important APIs, types, and functions
Includes `../../common`, `global-config-env.yaml`, `kernel-disk-pvc.yaml`, and `workflow-artifacts.yaml`. Applies patches adding nested-VM tolerations and node selectors to boot/fuzz/retest workflow templates, and replaces dashboard service annotations with a Google Cloud NEG annotation.

## Control flow
Production and staging GKE overlays build on this common layer, then provide concrete global config. Workflows are scheduled to nodes labeled for nested virtualization.

## State and persistence behavior
Adds cloud storage bindings for Spanner/GCS/artifacts and Filestore kernel repo storage.

## Dependencies and integration points
Depends on GKE node labels `amd64-nested-virtualization: "true"`, taint `workload=nested-vm:NoSchedule`, Google Cloud NEG controller, and workflow template names matching `(boot|fuzz|retest)-action-template`.

## Risks and edge cases
Regex target patches depend on Kustomize behavior and exact workflow template names. Missing node labels/taints can leave workflows unschedulable. The annotation patch replaces all existing service annotations.

## Test signals
Validated by GKE deployment/rendering and workflow scheduling, not local smoke.
