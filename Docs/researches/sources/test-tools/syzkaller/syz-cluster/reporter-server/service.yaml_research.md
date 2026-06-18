## sources/test-tools/syzkaller/syz-cluster/reporter-server/service.yaml

This Kubernetes `Service` exposes reporter-server pods selected by `app: reporter-server` on TCP port 8080 with targetPort 8080. The service type is `ClusterIP`, so it is internal to the cluster.

It integrates with other in-cluster components that call reporter APIs. Risks are limited to selector/port drift from the deployment and lack of external exposure by design.
