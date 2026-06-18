# sources/test-tools/syzkaller/syz-cluster/dashboard/kustomization.yaml

## Purpose
Defines the base Kustomize resources for the dashboard component.

## Important APIs, types, and functions
Kustomize `resources` includes `deployment.yaml` and `service.yaml` from the same directory.

## Control flow
When an overlay references `../../dashboard`, this file pulls both dashboard workload and service into the rendered manifest set.

## State and persistence behavior
No runtime state is defined here; the deployment and service files define pod behavior and networking.

## Dependencies and integration points
Integrated by `overlays/common/kustomization.yaml`, which composes controller, dashboard, series tracker, kernel disk, reporter server, workflow, and network policies.

## Risks and edge cases
Any missing resource filename breaks Kustomize rendering. The file intentionally keeps the base minimal and leaves environment-specific patching to overlays.

## Test signals
Exercised indirectly by `local_cluster_test.sh`, which applies the test overlay and verifies the web dashboard service responds.
