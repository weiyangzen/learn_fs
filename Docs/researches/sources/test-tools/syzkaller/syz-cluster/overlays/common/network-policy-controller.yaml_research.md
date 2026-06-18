# sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-controller.yaml

## Purpose
Allows selected syz-cluster components to reach controller pods.

## Important APIs, types, and functions
Defines `NetworkPolicy` `controller-access` selecting `app: controller`, with ingress allowed from pods labeled `app: series-tracker`, `app: email-reporter`, or `tier: workflow`.

## Control flow
Under default ingress deny, only these pod groups may initiate ingress to controller pods.

## State and persistence behavior
No persistence; network control only.

## Dependencies and integration points
Matches the controller service used by series tracker, email reporter job submissions, and Argo workflows such as fetch-kernels querying `/trees`.

## Risks and edge cases
Dashboard access to controller is not allowed here, likely because dashboard reads from DB/blob directly. Pod label drift breaks access. Ports are unrestricted for allowed sources.

## Test signals
Workflows and series tracker operation exercise this path; local smoke waits for controller deployment but does not deeply test all callers.
