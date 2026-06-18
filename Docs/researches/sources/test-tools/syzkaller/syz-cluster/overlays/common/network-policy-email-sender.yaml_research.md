# sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-email-sender.yaml

## Purpose
Allows outbound internet access for email-sending related pods.

## Important APIs, types, and functions
Defines two egress `NetworkPolicy` resources: `send-test-email-git-access` for `app: send-test-email` and `email-reporter-git-access` for `app: email-reporter`, both with unrestricted egress.

## Control flow
If egress isolation is active for these pods, the empty egress rule permits all destinations.

## State and persistence behavior
No persistence.

## Dependencies and integration points
Supports SMTP/dashapi/email sending and Lore git access from email reporter, plus test email tooling.

## Risks and edge cases
The policy is broad and allows all outbound traffic, not just SMTP/dashapi/lore. It only matters if an egress policy selects these pods; otherwise Kubernetes egress is allowed by default.

## Test signals
Email reporter tests use fake sender and do not validate network policy. Cluster-level email/lore operation validates it operationally.
