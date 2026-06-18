# sources/test-tools/syzkaller/syz-cluster/overlays/common/network-deny-all.yaml

## Purpose
Establishes a default ingress-deny baseline for pods in the default namespace.

## Important APIs, types, and functions
Defines `networking.k8s.io/v1` `NetworkPolicy` `default-deny-all` with empty `podSelector` and `policyTypes: Ingress`.

## Control flow
Once applied, all selected pods deny ingress unless another policy permits it.

## State and persistence behavior
No data state; controls network admission.

## Dependencies and integration points
Requires explicit ingress allow policies for controller, reporter-server, dashboard, fake GCS, Spanner emulator, and other services.

## Risks and edge cases
This policy denies only ingress, not egress. Components without matching allow policies become unreachable. Network policy enforcement depends on the cluster CNI.

## Test signals
Smoke tests catch major missing ingress paths such as dashboard/controller availability.
