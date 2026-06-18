# sources/test-tools/syzkaller/syz-cluster/overlays/local/common/network-policy-spanner.yaml

## Purpose
Allows selected pods to access the local Spanner emulator.

## Important APIs, types, and functions
Defines `NetworkPolicy` `cloud-spanner-access` selecting `app: cloud-spanner-emulator`, with ingress allowed from pods labeled `app: db-mgmt`, `app: controller`, `app: web-dashboard`, and `app: reporter`.

## Control flow
Under default ingress deny, only selected app pods can connect to emulator ports.

## State and persistence behavior
No persistence; controls network reachability.

## Dependencies and integration points
Supports migrations, controller, dashboard, and reporter data access in local clusters.

## Risks and edge cases
Label `app: reporter` must match actual reporter server or worker labels; if the component uses `app: reporter-server`, access may fail. Email reporter is not listed, likely because it uses reporter/controller APIs rather than direct DB.

## Test signals
Local smoke migration and dashboard availability validate at least db-mgmt/controller/dashboard access.
