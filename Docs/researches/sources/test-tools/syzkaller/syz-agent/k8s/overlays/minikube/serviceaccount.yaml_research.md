# sources/test-tools/syzkaller/syz-agent/k8s/overlays/minikube/serviceaccount.yaml

Purpose: local service account for syz-agent.

Important APIs/types/functions: Kubernetes `ServiceAccount` named `syz-agent-ksa`.

Control flow: included by minikube overlay so the base StatefulSet service account reference resolves locally.

State and persistence: Kubernetes service account object.

Dependencies and integration points: used by syz-agent StatefulSet.

Risks: no RBAC is shown here; default permissions apply unless bound elsewhere.

Test signals: pod startup without missing service account error.
