# sources/test-tools/syzkaller/syz-cluster/overlays/local/minikube/global-config.yaml

## Purpose
Local minikube/debug runtime configuration.

## Important APIs, types, and functions
Sets `URL: http://localhost`, `parallelWorkflows: 1`, a sample Lore archive, SMTP email reporting config, one `torvalds` tree, and a small set of fuzz targets/campaigns.

## Control flow
Local services use this config for low-concurrency development runs with fake/local infrastructure.

## State and persistence behavior
No state; controls local runtime behavior and external URLs.

## Dependencies and integration points
Used by minikube overlay's configMapGenerator. Requires SMTP config to be meaningful if email sending is exercised.

## Risks and edge cases
Some values are explicitly placeholder/debug values. External corpus/kernel URLs are still real network dependencies. Email settings may send if wired to a real SMTP service.

## Test signals
Useful for manual local deployment; automated smoke uses the local test overlay instead.
