# sources/test-tools/syzkaller/syz-cluster/controller/service.yaml

Purpose: internal Kubernetes Service for controller.

Important APIs/types/functions: `Service` `controller-service`.

Control flow: selects pods labeled `app: controller`, exposes TCP port 8080 to targetPort 8080 as ClusterIP.

State and persistence: cluster service object only.

Dependencies and integration points: fronts controller deployment for in-cluster callers.

Risks: no external exposure; external access requires ingress or port-forward elsewhere.

Test signals: service endpoints and API connectivity.
