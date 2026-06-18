# sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-git-access.yaml

## Purpose
Allows outbound internet/git access for components that pull repositories.

## Important APIs, types, and functions
Defines egress policies for `app: series-tracker` and `app: kernel-repo-update`, both allowing all egress.

## Control flow
When egress isolation applies, selected pods can reach remote git servers and related resources.

## State and persistence behavior
No persistence.

## Dependencies and integration points
Supports series tracker fetching patch series and kernel fetcher workflow fetching kernel trees.

## Risks and edge cases
Broad egress is less restrictive than necessary. The kernel fetch workflow template must label pods with `app: kernel-repo-update` somewhere for the policy to select them; the researched template only shows `tier: workflow`.

## Test signals
No direct tests. Runtime failures would appear as git fetch/network errors in series tracker or Argo workflow logs.
