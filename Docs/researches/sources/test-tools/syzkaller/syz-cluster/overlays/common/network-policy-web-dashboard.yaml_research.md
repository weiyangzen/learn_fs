# sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-web-dashboard.yaml

## Purpose
Allows ingress to the web dashboard pods.

## Important APIs, types, and functions
Defines `NetworkPolicy` `access-to-web-dashboard` in namespace `default`, selecting `app: web-dashboard`, allowing ingress from any source (`from: []`) to TCP port 8081.

## Control flow
Under default ingress deny, this opens the dashboard's container port to all sources in the policy scope.

## State and persistence behavior
No persistence.

## Dependencies and integration points
Matches dashboard `main.go` listening on 8081 and service target port 8081. GKE service exposes port 80 with NEG annotations.

## Risks and edge cases
Open ingress may be intended for public dashboard access, but exposure is broad at the network policy layer. Service/listener port drift would break access.

## Test signals
`local_cluster_test.sh` validates dashboard service reachability.
