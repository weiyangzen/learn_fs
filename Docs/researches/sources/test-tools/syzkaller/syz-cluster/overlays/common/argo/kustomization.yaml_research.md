# sources/test-tools/syzkaller/syz-cluster/overlays/common/argo/kustomization.yaml

## Purpose
Composes upstream Argo Workflows installation with syz-cluster RBAC and controller patches.

## Important APIs, types, and functions
Kustomize `resources` includes Argo Workflows v3.6.2 `install.yaml` from GitHub and local `workflow-roles.yaml`. Patches apply `patch-argo-controller.yaml` and `patch-workflow-controller-configmap.yaml`.

## Control flow
Rendering fetches or references the remote Argo install manifest, then overlays local service account and default workflow configuration changes.

## State and persistence behavior
Installs Argo controller resources and RBAC; no application data state is defined here.

## Dependencies and integration points
Used by local common overlay; GKE common appears to rely on common resources differently. Interacts with workflow templates, service accounts, artifact repositories, and network policies.

## Risks and edge cases
Remote URL pinning to version v3.6.2 is stable by version tag but still requires network access at render time unless cached. Argo upstream manifest changes under the same tag would be unexpected but high impact. Namespace/service-account assumptions must match patches.

## Test signals
Indirectly exercised by local cluster smoke test during infrastructure deployment.
