# sources/test-tools/syzkaller/syz-cluster/kernel-disk/fetch-kernels-template.yaml

## Purpose
Argo workflow template that queries configured kernel trees and fetches their branches/tags into a shared bare git repository.

## Important APIs, types, and functions
Defines `WorkflowTemplate` `fetch-kernels-workflow-template` with entrypoint `main`, workflow pod label `tier: workflow`, pod GC and TTL settings, default service account `argo-executor-ksa`, HTTP template `query-trees-template`, and container template `process-tree` using `kernel-fetcher-ksa` and `alpine/git:latest`.

## Control flow
`main` first runs `query-trees-template`, which issues `GET http://controller-service:8080/trees`. Then `iterate-trees` loops over `$.trees` from the JSON response and invokes `process-tree` for each item, continuing on failure. Each process step mounts `base-kernel-repo-pv-claim`, initializes a bare repository if needed, removes/readds the remote named by tree name, fetches the configured branch/tags into namespaced refs, and prints the latest commit.

## State and persistence behavior
Persistent git object/ref state is stored in the shared PVC mounted at `/repo.git`. The workflow deletes completed pods after 12 hours and workflow objects after 24 hours. It removes stale `packed-refs.lock` before fetches to recover from interrupted runs.

## Dependencies and integration points
Depends on controller `/trees`, Argo expression/jsonpath support, kernel fetcher service account/RBAC, network policy egress for `app: kernel-repo-update`, and the PVC from GKE/local overlays.

## Risks and edge cases
The container template does not explicitly label pods `app: kernel-repo-update`, while the egress policy selects that label; if Argo does not add it elsewhere, git egress may be denied under egress enforcement. The template uses shell interpolation of tree fields in remote names/URLs/branches; malformed config could break shell commands. Shared bare repo writes with parallelism 1 avoid concurrent fetches within one workflow but not necessarily across overlapping workflows.

## Test signals
No direct unit test. Kustomize smoke deploys resources; runtime correctness requires Argo/controller/network/storage integration.
