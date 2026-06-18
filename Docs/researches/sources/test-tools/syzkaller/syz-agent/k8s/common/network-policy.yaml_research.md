# sources/test-tools/syzkaller/syz-agent/k8s/common/network-policy.yaml

Purpose: network isolation policy for syz-agent pods.

Important APIs/types/functions: Kubernetes `NetworkPolicy` named `syz-agent-policy`.

Control flow: selects pods labeled `app: syz-agent`, denies all ingress, and allows all egress.

State and persistence: cluster policy state only.

Dependencies and integration points: requires a CNI that enforces NetworkPolicy and namespace `syz-agent`.

Risks: egress remains unrestricted, so it is isolation from inbound access rather than full containment.

Test signals: Kubernetes policy admission and connectivity behavior.
