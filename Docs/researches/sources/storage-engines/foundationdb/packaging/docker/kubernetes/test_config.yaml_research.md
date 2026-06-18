# sources/storage-engines/foundationdb/packaging/docker/kubernetes/test_config.yaml

Purpose: This Kubernetes manifest demonstrates running FoundationDB processes with the `fdb-kubernetes-monitor` image in a StatefulSet. It is explicitly a development/test example, not a recommended production deployment.

Important resources: The file defines a 5-replica StatefulSet with `foundationdb` and `foundationdb-sidecar` containers, a ConfigMap containing `fdb.cluster` and monitor `config.json`, a ServiceAccount, Role, and RoleBinding. It uses PVCs for data and emptyDir volumes for logs/shared binaries/dynamic config.

Control flow: The main container runs monitor mode with input dir and log path. The sidecar runs `--mode sidecar`, copies `fdbserver` and `fdbcli`, and writes shared binaries. The monitor config builds fdbserver arguments from environment variables and process numbers, including public/listen addresses, datadirs, locality, logs, and JSON trace format.

State and persistence behavior: StatefulSet PVCs persist `/var/fdb/data`; logs and shared binaries are ephemeral. The ConfigMap seed cluster file is initially empty, while runtime cluster file is under the data volume.

Dependencies and integration points: It integrates Kubernetes downward API, RBAC permissions on pods, `fdb-kubernetes-monitor`, sidecar binary sharing, and FoundationDB process configuration.

Risks: Image tags are fixed at `7.3.73` and may drift from built images. `runProcesses` is false in config, so behavior depends on monitor sidecar coordination. Tests should apply this manifest to a disposable namespace, verify pod readiness, binary copying, generated process args, RBAC sufficiency, and cluster formation.
