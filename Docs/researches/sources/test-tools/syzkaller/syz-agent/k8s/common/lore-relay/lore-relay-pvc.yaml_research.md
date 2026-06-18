# sources/test-tools/syzkaller/syz-agent/k8s/common/lore-relay/lore-relay-pvc.yaml

Purpose: persistent volume claim for lore-relay checkout/archive state.

Important APIs/types/functions: Kubernetes `PersistentVolumeClaim` named `lore-relay-pvc`.

Control flow: requests `ReadWriteOnce` storage of `32Gi` using storage class `standard`.

State and persistence: persists `/lore-repo` mounted by the lore-relay deployment.

Dependencies and integration points: bound by the lore-relay deployment volume.

Risks: storage class name is cluster-specific; `ReadWriteOnce` assumes single replica.

Test signals: Kubernetes PVC bind status.
