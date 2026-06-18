# sources/test-tools/syzkaller/syz-agent/k8s/common/syz-agent.yaml

Purpose: base StatefulSet for syz-agent workers.

Important APIs/types/functions: `StatefulSet` `syz-agent` with six replicas, privileged container, config and workdir mounts, host `/dev/kvm` and `/dev` mounts, and a `workdir` PVC template.

Control flow: each pod runs the syz-agent image with `-name=$(POD_NAME)` and config path, gets `POD_NAME` from Downward API, and mounts persistent `/app/workdir`.

State and persistence: each StatefulSet replica gets a 512Gi `ReadWriteOnce` workdir PVC used for cache/build/job state.

Dependencies and integration points: overlays provide config map, image tags, node placement, secrets/env, and service account existence.

Risks: privileged access plus host `/dev` mount is necessary for VM work but high impact. Resource requests/limits are large. HOME is forced to avoid git permission warnings.

Test signals: pod scheduling, PVC binding, KVM availability, and agent dashboard polling.
